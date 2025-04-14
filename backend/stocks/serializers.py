from rest_framework import serializers
from .models import Stock, Index

class StockSerializer(serializers.ModelSerializer):
    indices = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'indices']

class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = ['id', 'name']

class IndexDetailSerializer(serializers.ModelSerializer):
    stocks = StockSerializer(many=True, read_only=True)
    
    class Meta:
        model = Index
        fields = ['id', 'name', 'stocks']