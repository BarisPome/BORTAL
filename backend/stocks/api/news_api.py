# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/news_api.py

from django.shortcuts import get_object_or_404
from rest_framework import status
from .base_api import BaseAPIView
from ..models import News, Stock
from ..serializers.news_serializers import NewsSerializer

class StockNewsAPIView(BaseAPIView):
    """API endpoint for retrieving news related to a stock"""
    cache_timeout = 900  # Cache for 15 minutes
    
    def get(self, request, symbol=None):
        # Get recent news, optionally filtered by stock
        queryset = News.objects.all().order_by('-publication_date')
        
        if symbol:
            stock = get_object_or_404(Stock, symbol=symbol)
            queryset = queryset.filter(stocks=stock)
        
        # Parse limit parameter
        limit = request.query_params.get('limit', 20)
        try:
            limit = int(limit)
        except ValueError:
            return self.error_response("Invalid 'limit' parameter")
        
        news = queryset[:limit]
        serializer = NewsSerializer(news, many=True)
        
        return self.success_response(
            serializer.data,
            count=len(serializer.data)
        )