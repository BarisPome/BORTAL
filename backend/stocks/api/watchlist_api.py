# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/watchlist_api.py

from django.shortcuts import get_object_or_404
from rest_framework import status
from .base_api import BaseAPIView
from ..models import Watchlist, WatchlistItem, Stock, StockPrice

class WatchlistAPIView(BaseAPIView):
    """API endpoint for managing watchlists"""
    authentication_required = True
    use_transactions = True
    
    def get(self, request):
        """Get all watchlists for the current user"""
        watchlists = Watchlist.objects.filter(user=request.user)
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

            items = WatchlistItem.objects.filter(
                watchlist=watchlist
            ).select_related('stock')

            for item in items:
                stock = item.stock
                latest_price = StockPrice.objects.filter(
                    stock=stock
                ).order_by('-date').first()

                stock_data = {
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'notes': item.notes,
                    'added_at': item.added_at,
                }

                if latest_price:
                    # Convert Decimal to float for JSON
                    latest_close = float(latest_price.close)
                    stock_data['latest_price'] = {
                        'date': latest_price.date,
                        'price': latest_close,
                        'change': None,
                        'change_percent': None
                    }

                    prev_price = StockPrice.objects.filter(
                        stock=stock,
                        date__lt=latest_price.date
                    ).order_by('-date').first()

                    if prev_price:
                        prev_close = float(prev_price.close)
                        change = latest_close - prev_close
                        change_percent = (change / prev_close) * 100

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
            return self.error_response(
                "Watchlist name is required"
            )

        if Watchlist.objects.filter(
            user=request.user,
            name=name
        ).exists():
            return self.error_response(
                "A watchlist with this name already exists",
                status=status.HTTP_409_CONFLICT
            )

        watchlist = Watchlist.objects.create(
            user=request.user,
            name=name,
            description=description
        )

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
                continue

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
        watchlist = get_object_or_404(
            Watchlist,
            id=watchlist_id,
            user=request.user
        )

        if 'name' in request.data:
            watchlist.name = request.data['name']
        if 'description' in request.data:
            watchlist.description = request.data['description']
        if request.data.get('is_default'):
            Watchlist.objects.filter(
                user=request.user,
                is_default=True
            ).update(is_default=False)
            watchlist.is_default = True

        watchlist.save()

        if 'stocks' in request.data:
            if request.data.get('replace_all'):
                WatchlistItem.objects.filter(
                    watchlist=watchlist
                ).delete()

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
                    continue

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
        watchlist = get_object_or_404(
            Watchlist,
            id=watchlist_id,
            user=request.user
        )

        name = watchlist.name
        watchlist.delete()

        return self.success_response(
            message=f"Watchlist '{name}' deleted successfully"
        )



class WatchlistItemAPIView(BaseAPIView):
    """API endpoint for managing items in a watchlist"""
    authentication_required = True
    
    def post(self, request, watchlist_id):
        """Add a stock to a watchlist"""
        watchlist = get_object_or_404(
            Watchlist,
            id=watchlist_id,
            user=request.user
        )

        symbol = request.data.get('symbol')
        if not symbol:
            return self.error_response(
                "Stock symbol is required"
            )

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )

        if WatchlistItem.objects.filter(
            watchlist=watchlist,
            stock=stock
        ).exists():
            return self.error_response(
                f"Stock '{symbol}' is already in this watchlist",
                status=status.HTTP_409_CONFLICT
            )

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
        watchlist = get_object_or_404(
            Watchlist,
            id=watchlist_id,
            user=request.user
        )

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )

        deleted, _ = WatchlistItem.objects.filter(
            watchlist=watchlist,
            stock=stock
        ).delete()

        if deleted:
            return self.success_response(
                message=f"Removed {symbol} from watchlist"
            )
        return self.error_response(
            f"Stock '{symbol}' is not in this watchlist",
            status=status.HTTP_404_NOT_FOUND
        )
    
    def patch(self, request, watchlist_id, symbol):
        """Update notes for a stock in a watchlist"""
        watchlist = get_object_or_404(
            Watchlist,
            id=watchlist_id,
            user=request.user
        )

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self.error_response(
                f"Stock with symbol '{symbol}' not found",
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            item = WatchlistItem.objects.get(
                watchlist=watchlist,
                stock=stock
            )
        except WatchlistItem.DoesNotExist:
            return self.error_response(
                f"Stock '{symbol}' is not in this watchlist",
                status=status.HTTP_404_NOT_FOUND
            )

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
