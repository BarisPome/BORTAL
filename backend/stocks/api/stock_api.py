# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/stock_api.py

from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Avg, Max, Min
from rest_framework import status
from datetime import datetime, timedelta

from .base_api import BaseAPIView
from ..models import Stock, StockPrice, TechnicalIndicator
from ..serializers.stock_serializers import (
    StockListSerializer, StockDetailSerializer, 
    StockPriceSerializer, StockTechnicalSerializer
)

class StockListAPIView(BaseAPIView):
    """API endpoint for listing stocks with filtering options"""
    cache_timeout = 3600  # Cache for 1 hour
    
    def get(self, request):
        queryset = Stock.objects.all()
        
        # Apply filters if provided
        sector = request.query_params.get('sector')
        if sector:
            queryset = queryset.filter(sector__name=sector)
        
        index = request.query_params.get('index')
        if index:
            queryset = queryset.filter(indices__name=index)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(symbol__icontains=search) | 
                Q(name__icontains=search)
            )
        
        # Optional prefetch for better performance
        queryset = queryset.select_related('sector').prefetch_related('indices')
        
        # Apply ordering
        ordering = request.query_params.get('ordering', 'symbol')
        if ordering.startswith('-'):
            field = ordering[1:]
            queryset = queryset.order_by(F(field).desc(nulls_last=True))
        else:
            queryset = queryset.order_by(F(ordering).asc(nulls_last=True))
        
        # Simple pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = StockListSerializer(queryset[start:end], many=True)
        
        return self.success_response(
            serializer.data,
            pagination={
                'page': page,
                'page_size': page_size,
                'total_count': queryset.count()
            }
        )


class StockDetailAPIView(BaseAPIView):
    """API endpoint for retrieving detailed stock information"""
    cache_timeout = 900  # Cache for 15 minutes
    
    def get(self, request, symbol):
        stock = get_object_or_404(Stock, symbol=symbol)
        serializer = StockDetailSerializer(stock)
        return self.success_response(serializer.data)


class StockPriceAPIView(BaseAPIView):
    """API endpoint for retrieving stock price history"""
    cache_timeout = 1800  # Cache for 30 minutes
    
    def get(self, request, symbol):
        stock = get_object_or_404(Stock, symbol=symbol)
        
        # Parse date range parameters
        days = request.query_params.get('days')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Build the queryset based on parameters
        queryset = StockPrice.objects.filter(stock=stock)
        
        if days:
            try:
                days = int(days)
                min_date = datetime.now().date() - timedelta(days=days)
                queryset = queryset.filter(date__gte=min_date)
            except ValueError:
                return self.error_response("Invalid 'days' parameter")
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start)
            except ValueError:
                return self.error_response("Invalid 'start_date' format, use YYYY-MM-DD")
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end)
            except ValueError:
                return self.error_response("Invalid 'end_date' format, use YYYY-MM-DD")
        
        # Order by date
        prices = queryset.order_by('date')
        
        # Calculate intervals for large date ranges (reduce data points)
        if prices.count() > 500:
            # For example, return weekly data instead of daily
            interval = max(1, prices.count() // 500)
            prices = prices[::interval]
        
        serializer = StockPriceSerializer(prices, many=True)
        
        # Include some stats
        if prices.exists():
            stats = {
                'min_price': float(prices.aggregate(min=Min('low'))['min']),
                'max_price': float(prices.aggregate(max=Max('high'))['max']),
                'avg_volume': float(prices.aggregate(avg=Avg('volume'))['avg']),
                'start_date': prices.first().date.isoformat(),
                'end_date': prices.last().date.isoformat(),
                'data_points': len(serializer.data)
            }
        else:
            stats = {}
        
        return self.success_response(
            serializer.data,
            symbol=stock.symbol,
            name=stock.name,
            stats=stats
        )


class StockTechnicalAPIView(BaseAPIView):
    """API endpoint for retrieving technical indicators"""
    cache_timeout = 1800  # Cache for 30 minutes
    
    def get(self, request, symbol):
        stock = get_object_or_404(Stock, symbol=symbol)
        
        # Parse date range parameters
        days = request.query_params.get('days', 30)
        try:
            days = int(days)
            min_date = datetime.now().date() - timedelta(days=days)
        except ValueError:
            return self.error_response("Invalid 'days' parameter")
        
        # Get requested indicators (or all if not specified)
        indicators = request.query_params.get('indicators', '').split(',')
        indicators = [i.strip() for i in indicators if i.strip()]
        
        # Build the queryset
        queryset = TechnicalIndicator.objects.filter(
            stock=stock,
            date__gte=min_date
        ).order_by('date')
        
        # If no data, return empty with message
        if not queryset.exists():
            return self.success_response(
                [],
                message="No technical indicator data available for this stock"
            )
        
        # Serialize data
        serializer = StockTechnicalSerializer(queryset, many=True)
        data = serializer.data
        
        # Filter to only requested indicators if specified
        if indicators:
            filtered_data = []
            for item in data:
                filtered_item = {'date': item['date'], 'stock': item['stock']}
                for ind in indicators:
                    if ind in item:
                        filtered_item[ind] = item[ind]
                filtered_data.append(filtered_item)
            data = filtered_data
        
        return self.success_response(
            data,
            symbol=stock.symbol,
            name=stock.name
        )