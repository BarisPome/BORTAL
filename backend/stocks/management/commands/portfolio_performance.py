from decimal import Decimal
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, F, FloatField
from django.utils import timezone
from stocks.models import (
    Portfolio, PortfolioHolding, Stock, StockPrice,
    PortfolioTransaction, User
)


class Command(BaseCommand):
    help = "Calculate and track portfolio performance over time"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of historical data to calculate (default: 30)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Calculate performance for a specific user only'
        )
        parser.add_argument(
            '--portfolio',
            type=str,
            help='Calculate performance for a specific portfolio UUID only'
        )

    def handle(self, *args, **options):
        days = options['days']
        specific_user = options.get('user')
        specific_portfolio = options.get('portfolio')
        
        # Get portfolios to process
        if specific_portfolio:
            portfolios = Portfolio.objects.filter(id=specific_portfolio)
            if not portfolios.exists():
                self.stderr.write(f"❌ Portfolio with UUID '{specific_portfolio}' not found.")
                return
        elif specific_user:
            try:
                # Try as user ID first
                user_id = int(specific_user)
                user = User.objects.get(id=user_id)
            except (ValueError, User.DoesNotExist):
                # Then try as username
                try:
                    user = User.objects.get(username=specific_user)
                except User.DoesNotExist:
                    self.stderr.write(f"❌ User '{specific_user}' not found.")
                    return
            
            portfolios = Portfolio.objects.filter(user=user)
            if not portfolios.exists():
                self.stderr.write(f"❌ No portfolios found for user '{user.username}'.")
                return
        else:
            # Process all portfolios
            portfolios = Portfolio.objects.all()
            if not portfolios.exists():
                self.stderr.write("❌ No portfolios found in the system.")
                return
        
        self.stdout.write(f"🔍 Processing {portfolios.count()} portfolios...")
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Create a list of dates to analyze
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Process each portfolio
        for portfolio in portfolios:
            self.stdout.write(f"\n💼 Analyzing portfolio: {portfolio.name} (Owner: {portfolio.user.username})")
            
            # Get all transactions for this portfolio
            transactions = PortfolioTransaction.objects.filter(portfolio=portfolio)
            
            if not transactions.exists():
                self.stdout.write(f"  ℹ️ No transactions found for this portfolio, skipping")
                continue
            
            # Calculate performance for each date
            performance_data = []
            
            for date in date_range:
                # Get transactions up to this date
                transactions_until_date = transactions.filter(transaction_date__date__lte=date)
                
                if not transactions_until_date.exists():
                    # No transactions yet on this date
                    continue
                
                # Get distinct stocks in this portfolio as of this date
                stock_ids = transactions_until_date.values_list('stock', flat=True).distinct()
                stocks = Stock.objects.filter(id__in=stock_ids)
                
                # Calculate holdings for each stock as of this date
                total_value = Decimal('0')
                total_cost = Decimal('0')
                daily_holdings = []
                
                for stock in stocks:
                    # Get all transactions for this stock up to this date
                    stock_txs = transactions_until_date.filter(stock=stock)
                    
                    # Calculate position
                    quantity = Decimal('0')
                    cost = Decimal('0')
                    
                    for tx in stock_txs:
                        if tx.transaction_type == 'buy':
                            transaction_cost = tx.quantity * tx.price_per_unit + tx.fees
                            cost += transaction_cost
                            quantity += tx.quantity
                        elif tx.transaction_type == 'sell':
                            if quantity > 0:
                                # Calculate proportion of cost to remove
                                proportion_sold = min(tx.quantity / quantity, Decimal('1'))
                                cost_removed = cost * proportion_sold
                                cost -= cost_removed
                                quantity -= tx.quantity
                        elif tx.transaction_type == 'dividend':
                            # Dividends reduce cost basis
                            cost -= tx.quantity * tx.price_per_unit
                    
                    # Skip if no shares held
                    if quantity <= 0:
                        continue
                    
                    # Get the closest stock price on or before this date
                    try:
                        price = StockPrice.objects.filter(
                            stock=stock,
                            date__lte=date
                        ).order_by('-date').first()
                        
                        if price:
                            value = quantity * price.close
                            avg_cost = cost / quantity if quantity > 0 else Decimal('0')
                            
                            daily_holdings.append({
                                'symbol': stock.symbol,
                                'quantity': float(quantity),
                                'value': float(value),
                                'cost': float(cost),
                                'price': float(price.close),
                                'avg_cost': float(avg_cost),
                                'date': price.date.isoformat(),
                            })
                            
                            total_value += value
                            total_cost += cost
                    
                    except Exception as e:
                        self.stderr.write(f"  ⚠️ Error calculating value for {stock.symbol} on {date}: {str(e)}")
                
                # Skip days with no holdings or values
                if not daily_holdings or total_value == 0:
                    continue
                
                # Calculate performance metrics
                profit_loss = total_value - total_cost
                profit_loss_percent = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
                
                # Store daily performance
                performance_data.append({
                    'date': date.isoformat(),
                    'total_value': float(total_value),
                    'total_cost': float(total_cost),
                    'profit_loss': float(profit_loss),
                    'profit_loss_percent': float(profit_loss_percent),
                    'holdings': daily_holdings
                })
            
            # Skip portfolios with no calculable performance
            if not performance_data:
                self.stdout.write(f"  ⚠️ Could not calculate performance data for this portfolio")
                continue
            
            # Calculate additional metrics
            # Get first and last day with data
            first_day = performance_data[0]
            last_day = performance_data[-1]
            
            # Calculate overall return
            start_value = first_day['total_value']
            end_value = last_day['total_value']
            overall_return_percent = ((end_value - start_value) / start_value) * 100 if start_value > 0 else 0
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(performance_data)):
                prev_value = performance_data[i-1]['total_value']
                curr_value = performance_data[i]['total_value']
                if prev_value > 0:
                    daily_return = ((curr_value - prev_value) / prev_value) * 100
                    daily_returns.append(daily_return)
            
            # Calculate volatility (standard deviation of daily returns)
            volatility = 0
            if daily_returns:
                import numpy as np
                volatility = np.std(daily_returns)
            
            # Final performance summary
            summary = {
                'portfolio_id': str(portfolio.id),
                'portfolio_name': portfolio.name,
                'user_id': portfolio.user.id,
                'username': portfolio.user.username,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                },
                'metrics': {
                    'start_value': first_day['total_value'],
                    'end_value': last_day['total_value'],
                    'overall_return_percent': float(overall_return_percent),
                    'current_profit_loss': last_day['profit_loss'],
                    'current_profit_loss_percent': last_day['profit_loss_percent'],
                    'volatility': float(volatility)
                },
                'daily_performance': performance_data
            }
            
            # Store performance data in custom field
            portfolio.system_fields = {
                'performance': summary
            }
            portfolio.save()
            
            # Display summary to console
            self.stdout.write(f"  📊 Performance Summary (last {days} days):")
            self.stdout.write(f"    Start Value: {summary['metrics']['start_value']:.2f} {portfolio.currency}")
            self.stdout.write(f"    End Value: {summary['metrics']['end_value']:.2f} {portfolio.currency}")
            self.stdout.write(f"    Overall Return: {summary['metrics']['overall_return_percent']:.2f}%")
            self.stdout.write(f"    Current P/L: {summary['metrics']['current_profit_loss']:.2f} " +
                              f"({summary['metrics']['current_profit_loss_percent']:.2f}%)")
            
            # Get top performing holdings from the latest day
            latest_holdings = last_day['holdings']
            if latest_holdings:
                # Sort by profit/loss percent
                for holding in latest_holdings:
                    if holding['avg_cost'] > 0:
                        holding['pl_percent'] = ((holding['price'] - holding['avg_cost']) / holding['avg_cost']) * 100
                    else:
                        holding['pl_percent'] = 0
                
                # Get top and bottom performers
                sorted_holdings = sorted(latest_holdings, key=lambda x: x['pl_percent'], reverse=True)
                top_performers = sorted_holdings[:3]
                bottom_performers = sorted_holdings[-3:]
                
                self.stdout.write(f"    📈 Top Performers:")
                for holding in top_performers:
                    self.stdout.write(f"      {holding['symbol']}: {holding['pl_percent']:.2f}%")
                
                self.stdout.write(f"    📉 Bottom Performers:")
                for holding in bottom_performers:
                    self.stdout.write(f"      {holding['symbol']}: {holding['pl_percent']:.2f}%")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Portfolio performance analysis completed!"))