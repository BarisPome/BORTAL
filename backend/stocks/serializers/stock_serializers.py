from rest_framework import serializers
from ..models import Stock

class StockSerializer(serializers.ModelSerializer):
    indices = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'indices']