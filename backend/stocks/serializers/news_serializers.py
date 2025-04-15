# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/serializers/news_serializers.py

from rest_framework import serializers
from ..models import News
from .stock_serializers import StockListSerializer

class NewsSerializer(serializers.ModelSerializer):
    """Serializer for news items"""
    related_stocks = serializers.SerializerMethodField()
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'source', 'url', 'image_url', 
                  'publication_date', 'related_stocks']
    
    def get_related_stocks(self, obj):
        """Get stocks related to this news item"""
        return StockListSerializer(obj.stocks.all()[:5], many=True).data