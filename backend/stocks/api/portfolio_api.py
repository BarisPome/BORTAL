# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/portfolio_api.py

from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal

from .base_api import BaseAPIView
from ..models import Portfolio, PortfolioTransaction, PortfolioHolding, Stock, StockPrice, User
from ..serializers.portfolio_serializers import (
    PortfolioSerializer, PortfolioTransactionSerializer, 
    PortfolioHoldingSerializer, PortfolioCreateUpdateSerializer,
    TransactionCreateSerializer
)


class PortfolioListAPIView(BaseAPIView):
    """API endpoint for listing user portfolios"""
    authentication_required = True
    
    def get(self, request):
        """Get all portfolios for the current user"""
        portfolios = Portfolio.objects.filter(user=request.user)
        serializer = PortfolioSerializer(portfolios, many=True)
        
        # Add summary data for each portfolio
        data = []
        for portfolio_data in serializer.data:
            portfolio_id = portfolio_data['id']
            portfolio = Portfolio.objects.get(id=portfolio_id)
            
            # Calculate portfolio value
            total_value = Decimal('0')
            total_cost = Decimal('0')
            holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
            
            for holding in holdings:
                latest_price = StockPrice.objects.filter(stock=holding.stock).order_by('-date').first()
                if latest_price:
                    holding_value = holding.quantity * latest_price.close
                    holding_cost = holding.quantity * holding.average_cost
                    total_value += holding_value
                    total_cost += holding_cost
            
            # Calculate profit/loss
            profit_loss = total_value - total_cost
            profit_loss_percent = (profit_loss / total_cost * 100) if total_cost > 0 else 0
            
            # Add summary to portfolio data
            portfolio_data['summary'] = {
                'total_value': float(total_value),
                'total_cost': float(total_cost),
                'profit_loss': float(profit_loss),
                'profit_loss_percent': float(profit_loss_percent),
                'holding_count': holdings.count()
            }
            
            data.append(portfolio_data)
        
        return self.success_response(data)
    
    def post(self, request):
        """Create a new portfolio"""
        serializer = PortfolioCreateUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                "Invalid portfolio data",
                errors=serializer.errors
            )
        
        # Check if a portfolio with this name already exists
        if Portfolio.objects.filter(user=request.user, name=serializer.validated_data['name']).exists():
            return self.error_response(
                "A portfolio with this name already exists",
                status=status.HTTP_409_CONFLICT
            )
        
        # If this is marked as default, unset any other default portfolio
        if serializer.validated_data.get('is_default', False):
            Portfolio.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Create the portfolio
        portfolio = Portfolio.objects.create(
            user=request.user,
            **serializer.validated_data
        )
        
        return self.success_response(
            PortfolioSerializer(portfolio).data,
            message="Portfolio created successfully",
            status=status.HTTP_201_CREATED
        )


class PortfolioDetailAPIView(BaseAPIView):
    """API endpoint for retrieving, updating, or deleting a portfolio"""
    authentication_required = True
    use_transactions = True
    
    def get(self, request, portfolio_id):
        """Get detailed information about a portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        serializer = PortfolioSerializer(portfolio)
        portfolio_data = serializer.data
        
        # Get holdings
        holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
        holdings_serializer = PortfolioHoldingSerializer(holdings, many=True)
        portfolio_data['holdings'] = holdings_serializer.data
        
        # Calculate portfolio summary
        total_value = Decimal('0')
        total_cost = Decimal('0')
        
        for holding in holdings:
            latest_price = StockPrice.objects.filter(stock=holding.stock).order_by('-date').first()
            if latest_price:
                holding_value = holding.quantity * latest_price.close
                holding_cost = holding.quantity * holding.average_cost
                total_value += holding_value
                total_cost += holding_cost
        
        # Calculate profit/loss
        profit_loss = total_value - total_cost
        profit_loss_percent = (profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Add summary to response
        portfolio_data['summary'] = {
            'total_value': float(total_value),
            'total_cost': float(total_cost),
            'profit_loss': float(profit_loss),
            'profit_loss_percent': float(profit_loss_percent),
            'holding_count': holdings.count()
        }
        
        # Get recent transactions
        transactions = PortfolioTransaction.objects.filter(portfolio=portfolio).order_by('-transaction_date')[:10]
        transactions_serializer = PortfolioTransactionSerializer(transactions, many=True)
        portfolio_data['recent_transactions'] = transactions_serializer.data
        
        # Get performance data if available
        if hasattr(portfolio, 'system_fields') and portfolio.system_fields:
            try:
                performance = portfolio.system_fields.get('performance', {})
                if performance:
                    portfolio_data['performance'] = performance
            except (AttributeError, KeyError):
                pass
        
        return self.success_response(portfolio_data)
    
    def put(self, request, portfolio_id):
        """Update a portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        serializer = PortfolioCreateUpdateSerializer(data=request.data, partial=True)
        
        if not serializer.is_valid():
            return self.error_response(
                "Invalid portfolio data",
                errors=serializer.errors
            )
        
        # Check if updating name and if that name already exists for another portfolio
        if 'name' in serializer.validated_data and serializer.validated_data['name'] != portfolio.name:
            if Portfolio.objects.filter(user=request.user, name=serializer.validated_data['name']).exists():
                return self.error_response(
                    "Another portfolio with this name already exists",
                    status=status.HTTP_409_CONFLICT
                )
        
        # If setting as default, unset any other default portfolio
        if serializer.validated_data.get('is_default', False) and not portfolio.is_default:
            Portfolio.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Update the portfolio
        for key, value in serializer.validated_data.items():
            setattr(portfolio, key, value)
        
        portfolio.save()
        
        return self.success_response(
            PortfolioSerializer(portfolio).data,
            message="Portfolio updated successfully"
        )
    
    def delete(self, request, portfolio_id):
        """Delete a portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        # Prevent deletion of the only default portfolio
        if portfolio.is_default and Portfolio.objects.filter(user=request.user).count() == 1:
            return self.error_response(
                "Cannot delete the only portfolio. Create another portfolio first.",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        portfolio_name = portfolio.name
        portfolio.delete()
        
        return self.success_response(
            message=f"Portfolio '{portfolio_name}' deleted successfully"
        )


class PortfolioTransactionAPIView(BaseAPIView):
    """API endpoint for managing portfolio transactions"""
    authentication_required = True
    use_transactions = True
    
    def get(self, request, portfolio_id):
        """Get all transactions for a portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        # Parse filters
        transaction_type = request.query_params.get('type')
        symbol = request.query_params.get('symbol')
        
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        days = request.query_params.get('days')
        
        # Build query
        queryset = PortfolioTransaction.objects.filter(portfolio=portfolio)
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if symbol:
            queryset = queryset.filter(stock__symbol=symbol)
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(transaction_date__date__gte=start)
            except ValueError:
                return self.error_response("Invalid start_date format, use YYYY-MM-DD")
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(transaction_date__date__lte=end)
            except ValueError:
                return self.error_response("Invalid end_date format, use YYYY-MM-DD")
        
        if days and not (start_date or end_date):
            try:
                days = int(days)
                min_date = datetime.now().date() - timedelta(days=days)
                queryset = queryset.filter(transaction_date__date__gte=min_date)
            except ValueError:
                return self.error_response("Invalid days parameter, must be an integer")
        
        # Order by date, most recent first
        transactions = queryset.order_by('-transaction_date')
        
        # Apply pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_transactions = transactions[start:end]
        serializer = PortfolioTransactionSerializer(paginated_transactions, many=True)
        
        return self.success_response(
            serializer.data,
            pagination={
                'page': page,
                'page_size': page_size,
                'total_count': transactions.count()
            }
        )
    
    def post(self, request, portfolio_id):
        """Add a new transaction to the portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        serializer = TransactionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                "Invalid transaction data",
                errors=serializer.errors
            )
        
        # Get the stock object
        stock_symbol = serializer.validated_data.pop('stock_symbol')
        stock = Stock.objects.get(symbol=stock_symbol)
        
        # If this is a sell transaction, make sure there are enough shares
        if serializer.validated_data['transaction_type'] == 'sell':
            # Calculate current holding
            current_quantity = self._get_current_quantity(portfolio, stock)
            
            if current_quantity < serializer.validated_data['quantity']:
                return self.error_response(
                    f"Insufficient shares for sale. Current holding: {current_quantity}",
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create the transaction
        transaction = PortfolioTransaction.objects.create(
            portfolio=portfolio,
            stock=stock,
            **serializer.validated_data
        )
        
        # Update the portfolio holdings
        self._update_portfolio_holdings(portfolio, stock)
        
        return self.success_response(
            PortfolioTransactionSerializer(transaction).data,
            message="Transaction added successfully",
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request, portfolio_id, transaction_id):
        """Delete a transaction"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        transaction = get_object_or_404(PortfolioTransaction, id=transaction_id, portfolio=portfolio)
        
        # Store the stock for recalculating holdings after deletion
        stock = transaction.stock
        
        # Delete the transaction
        transaction.delete()
        
        # Update the portfolio holdings
        self._update_portfolio_holdings(portfolio, stock)
        
        return self.success_response(
            message="Transaction deleted successfully"
        )
    
    def _get_current_quantity(self, portfolio, stock):
        """Calculate the current quantity of a stock in the portfolio"""
        buys = PortfolioTransaction.objects.filter(
            portfolio=portfolio,
            stock=stock,
            transaction_type='buy'
        ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']
        
        sells = PortfolioTransaction.objects.filter(
            portfolio=portfolio,
            stock=stock,
            transaction_type='sell'
        ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']
        
        return buys - sells
    
    def _update_portfolio_holdings(self, portfolio, stock):
        """Recalculate and update the portfolio holdings for a stock"""
        transactions = PortfolioTransaction.objects.filter(
            portfolio=portfolio,
            stock=stock
        ).order_by('transaction_date')
        
        # Initialize counters
        quantity = Decimal('0')
        total_cost = Decimal('0')
        
        # Process each transaction
        for tx in transactions:
            if tx.transaction_type == 'buy':
                transaction_cost = tx.quantity * tx.price_per_unit + tx.fees
                total_cost += transaction_cost
                quantity += tx.quantity
            elif tx.transaction_type == 'sell':
                if quantity > 0:
                    # Calculate proportion of cost to remove
                    proportion_sold = min(tx.quantity / quantity, Decimal('1'))
                    cost_removed = total_cost * proportion_sold
                    total_cost -= cost_removed
                    quantity -= tx.quantity
            elif tx.transaction_type == 'dividend':
                # Dividends reduce cost basis
                total_cost -= tx.quantity * tx.price_per_unit
        
        # Update or delete the holding
        if quantity > 0:
            average_cost = total_cost / quantity
            
            PortfolioHolding.objects.update_or_create(
                portfolio=portfolio,
                stock=stock,
                defaults={
                    'quantity': quantity,
                    'average_cost': average_cost
                }
            )
        else:
            # Remove the holding if quantity is zero
            PortfolioHolding.objects.filter(portfolio=portfolio, stock=stock).delete()


class PortfolioPerformanceAPIView(BaseAPIView):
    """API endpoint for retrieving portfolio performance data"""
    authentication_required = True
    cache_timeout = 900  # Cache for 15 minutes
    
    def get(self, request, portfolio_id):
        """Get performance data for a portfolio"""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        # Check if performance data is available
        if not hasattr(portfolio, 'system_fields') or not portfolio.system_fields:
            # Run the calculation command if no data is available
            from django.core.management import call_command
            try:
                call_command('portfolio_performance', portfolio=str(portfolio.id), days=90)
                # Refresh the portfolio object to get updated data
                portfolio = Portfolio.objects.get(id=portfolio_id)
            except Exception as e:
                return self.error_response(
                    "Could not calculate portfolio performance",
                    error_details=str(e)
                )
        
        # Extract performance data
        try:
            performance = portfolio.system_fields.get('performance', {})
            if not performance:
                return self.error_response(
                    "No performance data available for this portfolio"
                )
            
            return self.success_response(performance)
            
        except (AttributeError, KeyError):
            return self.error_response(
                "No performance data available for this portfolio"
            )