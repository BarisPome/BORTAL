# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/api/sector_api.py

from django.db.models import Count
from .base_api import BaseAPIView
from ..models import Sector
from ..serializers.sector_serializers import SectorSerializer

class SectorListAPIView(BaseAPIView):
    """API endpoint for listing sectors"""
    cache_timeout = 3600  # Cache for 1 hour
    
    def get(self, request):
        sectors = Sector.objects.annotate(stock_count=Count('stocks')).order_by('name')
        serializer = SectorSerializer(sectors, many=True)
        return self.success_response(serializer.data)