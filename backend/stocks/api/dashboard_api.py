from django.db.models import Count, Avg, Max, Min, F, Q, Sum
from rest_framework import serializers, status
from rest_framework.response import Response
from datetime import datetime, timedelta
import json

from .base_api import BaseAPIView
from stocks.models import (
    Stock, Index, StockPrice, News, Watchlist, Portfolio,
    PortfolioHolding, SystemSetting, UserActivity
)


class DashboardAPIView(BaseAPIView):
    """API endpoint for retrieving dashboard data"""
    authentication_required = False  # Temporarily set to False for testing
    cache_timeout = 300  # Cache for 5 minutes
    
    def get(self, request):
        """
        Get aggregated dashboard data including:
        - Market overview
        - User's watchlists
        - User's portfolios
        - Recent news
        - Most viewed stocks
        """
        try:
            # Get user's data
            user = request.user
            
            # For debugging authentication issues
            if not user.is_authenticated and self.authentication_required:
                return Response(
                    {"error": "Authentication required", "detail": "Please log in to access this endpoint"}, 
                    status=401
                )
            
            # Prepare dashboard data
            dashboard_data = {}
            
            try:
                dashboard_data['market_overview'] = self._get_market_overview()
            except Exception as e:
                import traceback
                print(f"Error in _get_market_overview: {str(e)}")
                print(traceback.format_exc())
                dashboard_data['market_overview'] = {"error": str(e)}
            
            try:
                dashboard_data['user_watchlists'] = self._get_user_watchlists(user)
            except Exception as e:
                print(f"Error in _get_user_watchlists: {str(e)}")
                dashboard_data['user_watchlists'] = []
            
            try:
                dashboard_data['user_portfolios'] = self._get_user_portfolios(user)
            except Exception as e:
                print(f"Error in _get_user_portfolios: {str(e)}")
                dashboard_data['user_portfolios'] = []
            
            try:
                dashboard_data['recent_news'] = self._get_recent_news()
            except Exception as e:
                print(f"Error in _get_recent_news: {str(e)}")
                dashboard_data['recent_news'] = []
            
            try:
                dashboard_data['most_viewed'] = self._get_most_viewed_stocks(user)
            except Exception as e:
                print(f"Error in _get_most_viewed_stocks: {str(e)}")
                dashboard_data['most_viewed'] = []
            
            # Record user activity - only if authenticated
            if user.is_authenticated:
                try:
                    UserActivity.objects.create(
                        user=user,
                        activity_type='view',
                        resource_type='dashboard',
                        details={'view_type': 'dashboard_home'}
                    )
                except Exception as e:
                    print(f"Error recording user activity: {str(e)}")
            
            return self.success_response(dashboard_data)
        except Exception as e:
            import traceback
            print(f"Error in DashboardAPIView: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": "An internal error occurred", "detail": str(e)}, 
                status=500
            )
    
    def _get_market_overview(self):
        """Get market overview data"""
        # Get main indices
        indices_data = []
        main_indices = ['BIST100', 'BIST30', 'BIST50']
        
        for index_name in main_indices:
            try:
                index = Index.objects.get(name=index_name)
                latest_price = index.prices.order_by('-date').first()
                prev_price = index.prices.filter(date__lt=latest_price.date).order_by('-date').first() if latest_price else None
                
                if latest_price and prev_price:
                    change = float(latest_price.close - prev_price.close)
                    change_percent = float((latest_price.close - prev_price.close) / prev_price.close * 100)
                    
                    indices_data.append({
                        'name': index.name,
                        'display_name': index.display_name or index.name,
                        'last_price': float(latest_price.close),
                        'change': change,
                        'change_percent': change_percent,
                        'date': latest_price.date.isoformat()
                    })
            except (Index.DoesNotExist, AttributeError):
                continue
        
        # Get top gainers and losers
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get stocks with prices on both days
        stocks_with_prices = StockPrice.objects.filter(
            date__gte=yesterday,
            date__lte=today
        ).values('stock').annotate(count=Count('id')).filter(count__gte=2)
        
        stock_ids = [item['stock'] for item in stocks_with_prices]
        stocks = Stock.objects.filter(id__in=stock_ids)
        
        # Calculate price changes
        stock_changes = []
        
        for stock in stocks:
            latest = StockPrice.objects.filter(stock=stock).order_by('-date').first()
            prev = StockPrice.objects.filter(stock=stock, date__lt=latest.date).order_by('-date').first()
            
            if latest and prev and prev.close > 0:
                change_percent = float((latest.close - prev.close) / prev.close * 100)
                
                stock_changes.append({
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'price': float(latest.close),
                    'change_percent': change_percent
                })
        
        # Sort to get top gainers and losers
        stock_changes.sort(key=lambda x: x['change_percent'], reverse=True)
        top_gainers = stock_changes[:5]  # Top 5 gainers
        top_losers = stock_changes[-5:]  # Top 5 losers (reverse to show biggest losers first)
        top_losers.reverse()
        
        # Get market statistics
        advancing = sum(1 for stock in stock_changes if stock['change_percent'] > 0)
        declining = sum(1 for stock in stock_changes if stock['change_percent'] < 0)
        unchanged = sum(1 for stock in stock_changes if stock['change_percent'] == 0)
        
        # Get sector performance
        sector_performance = []
        
        # Return market overview data
        return {
            'indices': indices_data,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'market_stats': {
                'advancing': advancing,
                'declining': declining,
                'unchanged': unchanged,
                'total_stocks': len(stock_changes)
            },
            'as_of': datetime.now().isoformat()
        }
    
    def _get_user_watchlists(self, user):
        """Get user's watchlists summary"""
        watchlists = Watchlist.objects.filter(user=user)
        watchlists_data = []
        
        for watchlist in watchlists:
            # Get top performing stocks in watchlist
            items = watchlist.stocks.all()[:5]  # Limit to 5 stocks
            stocks_data = []
            
            for stock in items:
                latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                prev_price = StockPrice.objects.filter(stock=stock, date__lt=latest_price.date).order_by('-date').first() if latest_price else None
                
                if latest_price and prev_price and prev_price.close > 0:
                    change_percent = float((latest_price.close - prev_price.close) / prev_price.close * 100)
                    
                    stocks_data.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': float(latest_price.close),
                        'change_percent': change_percent
                    })
            
            # Sort by performance
            stocks_data.sort(key=lambda x: x['change_percent'], reverse=True)
            
            watchlists_data.append({
                'id': watchlist.id,
                'name': watchlist.name,
                'is_default': watchlist.is_default,
                'stock_count': watchlist.stocks.count(),
                'top_stocks': stocks_data
            })
        
        return watchlists_data
    
    def _get_user_portfolios(self, user):
        """Get user's portfolios summary"""
        portfolios = Portfolio.objects.filter(user=user)
        portfolios_data = []
        
        for portfolio in portfolios:
            # Calculate portfolio value
            total_value = 0
            total_cost = 0
            holdings = PortfolioHolding.objects.filter(portfolio=portfolio)
            
            for holding in holdings:
                latest_price = StockPrice.objects.filter(stock=holding.stock).order_by('-date').first()
                if latest_price:
                    holding_value = float(holding.quantity * latest_price.close)
                    holding_cost = float(holding.quantity * holding.average_cost)
                    total_value += holding_value
                    total_cost += holding_cost
            
            # Calculate profit/loss
            profit_loss = total_value - total_cost
            profit_loss_percent = (profit_loss / total_cost * 100) if total_cost > 0 else 0
            
            # Get top holdings
            top_holdings = []
            for holding in holdings[:5]:  # Limit to top 5
                latest_price = StockPrice.objects.filter(stock=holding.stock).order_by('-date').first()
                if latest_price:
                    holding_value = float(holding.quantity * latest_price.close)
                    weight = (holding_value / total_value * 100) if total_value > 0 else 0
                    
                    top_holdings.append({
                        'symbol': holding.stock.symbol,
                        'name': holding.stock.name,
                        'value': holding_value,
                        'weight': weight,
                        'quantity': float(holding.quantity)
                    })
            
            # Sort by value
            top_holdings.sort(key=lambda x: x['value'], reverse=True)
            
            portfolios_data.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'is_default': portfolio.is_default,
                'currency': portfolio.currency,
                'total_value': total_value,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'holding_count': holdings.count(),
                'top_holdings': top_holdings
            })
        
        return portfolios_data
    
    def _get_recent_news(self):
        """Get recent market news"""
        news = News.objects.all().order_by('-publication_date')[:10]
        news_data = []
        
        for item in news:
            news_data.append({
                'id': item.id,
                'title': item.title,
                'source': item.source,
                'date': item.publication_date.isoformat(),
                'url': item.url,
                'image_url': item.image_url
            })
        
        return news_data
    
    def _get_most_viewed_stocks(self, user):
        """Get most viewed stocks by the user"""
        # First try to get user's recently viewed stocks
        user_views = UserActivity.objects.filter(
            user=user,
            activity_type='view',
            resource_type='stock'
        ).order_by('-created_at')[:10]
        
        viewed_stock_ids = []
        for activity in user_views:
            if activity.resource_id and activity.resource_id not in viewed_stock_ids:
                viewed_stock_ids.append(activity.resource_id)
        
        # If user hasn't viewed many stocks, supplement with popular stocks
        if len(viewed_stock_ids) < 5:
            # Get generally popular stocks
            popular_views = UserActivity.objects.filter(
                activity_type='view',
                resource_type='stock'
            ).values('resource_id').annotate(
                view_count=Count('id')
            ).order_by('-view_count')[:10]
            
            for item in popular_views:
                if item['resource_id'] and item['resource_id'] not in viewed_stock_ids:
                    viewed_stock_ids.append(item['resource_id'])
        
        # If still not enough, add some default BIST30 stocks
        if len(viewed_stock_ids) < 5:
            try:
                bist30 = Stock.objects.filter(indices__name='BIST30')[:10]
                for stock in bist30:
                    if stock.id not in viewed_stock_ids:
                        viewed_stock_ids.append(stock.id)
            except Exception:
                pass
        
        # Get stock data
        viewed_stocks = []
        for stock_id in viewed_stock_ids[:10]:  # Limit to 10
            try:
                stock = Stock.objects.get(id=stock_id)
                latest_price = StockPrice.objects.filter(stock=stock).order_by('-date').first()
                
                if latest_price:
                    prev_price = StockPrice.objects.filter(
                        stock=stock, 
                        date__lt=latest_price.date
                    ).order_by('-date').first()
                    
                    change_percent = 0
                    if prev_price and prev_price.close > 0:
                        change_percent = float((latest_price.close - prev_price.close) / prev_price.close * 100)
                    
                    viewed_stocks.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'sector': stock.sector.name if stock.sector else None,
                        'price': float(latest_price.close),
                        'change_percent': change_percent,
                        'date': latest_price.date.isoformat()
                    })
            except (Stock.DoesNotExist, AttributeError):
                continue
        
        return viewed_stocks