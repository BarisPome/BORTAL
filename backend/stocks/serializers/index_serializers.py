from rest_framework import serializers
from ..models import Index

class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = ['id', 'name']

class IndexDetailSerializer(serializers.ModelSerializer):
    from .stock_serializers import StockSerializer
    stocks = StockSerializer(many=True, read_only=True)
    
    class Meta:
        model = Index
        fields = ['id', 'name', 'stocks']