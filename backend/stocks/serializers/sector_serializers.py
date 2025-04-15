# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/serializers/sector_serializers.py

from rest_framework import serializers
from ..models import Sector

class SectorSerializer(serializers.ModelSerializer):
    """Serializer for stock sectors"""
    stock_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sector
        fields = ['id', 'name', 'display_name', 'description', 'stock_count']