# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/index_api.py

from django.db.models import Count
from .base_api import BaseAPIView
from ..models import Index
from ..serializers.index_serializers import IndexSerializer

class IndexListAPIView(BaseAPIView):
    """API endpoint for listing market indices"""
    cache_timeout = 3600  # Cache for 1 hour
    
    def get(self, request):
        indices = Index.objects.annotate(stock_count=Count('stocks')).order_by('name')
        serializer = IndexSerializer(indices, many=True)
        return self.success_response(serializer.data)