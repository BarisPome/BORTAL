# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/watchlist_api.py

from django.shortcuts import get_object_or_404
from rest_framework import status
from .base_api import BaseAPIView
from ..models import Watchlist, WatchlistItem, Stock, StockPrice
from ..serializers.watchlist_serializers import WatchlistSerializer

class WatchlistAPIView(BaseAPIView):
    """API endpoint for managing watchlists"""
    authentication_required = True
    use_transactions = True
    
    def get(self, request):
        """Get all watchlists for the current user"""
        watchlists = Watchlist.objects.filter(user=request.user)
        
        # Prepare response data manually for custom formatting
        data = []
        for watchlist in watchlists:
            watchlist_data = {
                'id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'is_default': watchlist.is_default,
                'created_at': watchlist.created_at,
                'stocks': []
            }
            
            # Get all stock items with their latest prices
            items = WatchlistItem.objects.filter(watchlist=watchlist).select_related('stock')
            
            for item in items:
                stock = item.stock
                latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                
                stock_data = {
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'notes': item.notes,
                    'added_at': item.added_at,
                }
                
                if latest_price:
                    stock_data['latest_price'] = {
                        'date': latest_price.date,
                        'price': float(latest_price.close),
                        'change': None,
                        'change_percent': None
                    }
                    
                    # Get previous day's price for change calculation
                    prev_price = StockPrice.objects.filter(
                        stock=stock, 
                        date__lt=latest_price.date
                    ).order_by('-date').first()
                    
                    if prev_price:
                        change = float(latest_price.close - prev_price.close)
                        change_percent = float(change / prev_price.close * 100)
                        stock_data['latest_price']['change'] = change
                        stock_data['latest_price']['change_percent'] = change_percent
                
                watchlist_data['stocks'].append(stock_data)
            
            data.append(watchlist_data)
        
        return self.success_response(data)
    
    def post(self, request):
        """Create a new watchlist"""
        name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not name:
            return self.error_response("Watchlist name is required")
        
        # Check if a watchlist with this name already exists
        if Watchlist.objects.filter(user=request.user, name=name).exists():
            return self.error_response(
                "A watchlist with this name already exists",
                status=status.HTTP_409_CONFLICT
            )
        
        # Create the watchlist
        watchlist = Watchlist.objects.create(
            user=request.user,
            name=name,
            description=description
        )
        
        # Add initial stocks if provided
        stock_symbols = request.data.get('stocks', [])
        added_stocks = []
        
        for symbol in stock_symbols:
            try:
                stock = Stock.objects.get(symbol=symbol)
                WatchlistItem.objects.create(
                    watchlist=watchlist,
                    stock=stock
                )
                added_stocks.append(symbol)
            except Stock.DoesNotExist:
                pass  # Skip non-existent stocks
        
        return self.success_response(
            {
                'id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'added_stocks': added_stocks
            },
            message="Watchlist created successfully",
            status=status.HTTP_201_CREATED
        )
    
    def put(self, request, watchlist_id):
        """Update an existing watchlist"""
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        
        # Update fields if provided
        if 'name' in request.data:
            watchlist.name = request.data['name']
        
        if 'description' in request.data:
            watchlist.description = request.data['description']
        
        if 'is_default' in request.data and request.data['is_default']:
            # If setting as default, unset any other default watchlist
            Watchlist.objects.filter(user=request.user, is_default=True).update(is_default=False)
            watchlist.is_default = True
        
        watchlist.save()
        
        # Update stocks if provided
        if 'stocks' in request.data:
            # Clear existing items if replace_all is set
            if request.data.get('replace_all', False):
                WatchlistItem.objects.filter(watchlist=watchlist).delete()
            
            # Add new stocks
            added_stocks = []
            for symbol in request.data['stocks']:
                try:
                    stock = Stock.objects.get(symbol=symbol)
                    WatchlistItem.objects.get_or_create(
                        watchlist=watchlist,
                        stock=stock
                    )
                    added_stocks.append(symbol)
                except Stock.DoesNotExist:
                    pass  # Skip non-existent stocks
        
            return self.success_response(
                {
                    'id': watchlist.id,
                    'name': watchlist.name,
                    'added_stocks': added_stocks
                },
                message="Watchlist updated successfully"
            )
        
        return self.success_response(
            {
                'id': watchlist.id,
                'name': watchlist.name
            },
            message="Watchlist updated successfully"
        )
    
    def delete(self, request, watchlist_id):
        """Delete a watchlist"""
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        
        # Don't allow deleting the default watchlist if it's the only one
        if watchlist.is_default and Watchlist.objects.filter(user=request.user).count() == 1:
            return self.error_response(
                "Cannot delete the only watchlist. Create another watchlist first.",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        watchlist_name = watchlist.name
        watchlist.delete()
        
        return self.success_response(
            message=f"Watchlist '{watchlist_name}' deleted successfully"
        )


class WatchlistItemAPIView(BaseAPIView):
    """API endpoint for managing items in a watchlist"""
    authentication_required = True
    
    def post(self, request, watchlist_id):
        """Add a stock to a watchlist"""
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        
        symbol = request.data.get('symbol')
        if not symbol:
            return self.error_response("Stock symbol is required")
        
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already in watchlist
        if WatchlistItem.objects.filter(watchlist=watchlist, stock=stock).exists():
            return self.error_response(
                f"Stock '{symbol}' is already in this watchlist",
                status=status.HTTP_409_CONFLICT
            )
        
        # Add to watchlist
        item = WatchlistItem.objects.create(
            watchlist=watchlist,
            stock=stock,
            notes=request.data.get('notes', '')
        )
        
        return self.success_response(
            {
                'watchlist_id': watchlist.id,
                'stock_symbol': stock.symbol,
                'stock_name': stock.name,
                'added_at': item.added_at
            },
            message=f"Added {stock.symbol} to watchlist",
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request, watchlist_id, symbol):
        """Remove a stock from a watchlist"""
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Try to delete the item
        deleted, _ = WatchlistItem.objects.filter(watchlist=watchlist, stock=stock).delete()
        
        if deleted:
            return self.success_response(
                message=f"Removed {symbol} from watchlist"
            )
        else:
            return self.error_response(
                f"Stock '{symbol}' is not in this watchlist",
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, watchlist_id, symbol):
        """Update notes for a stock in a watchlist"""
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
        
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            item = WatchlistItem.objects.get(watchlist=watchlist, stock=stock)
        except WatchlistItem.DoesNotExist:
            return self.error_response(
                f"Stock '{symbol}' is not in this watchlist",
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update notes
        item.notes = request.data.get('notes', '')
        item.save()
        
        return self.success_response(
            {
                'watchlist_id': watchlist.id,
                'stock_symbol': stock.symbol,
                'notes': item.notes
            },
            message="Stock notes updated"
        )