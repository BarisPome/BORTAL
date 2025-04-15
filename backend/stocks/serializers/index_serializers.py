# index_serializers.py

from rest_framework import serializers
from ..models import Index

class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = ['id', 'name']

class IndexDetailSerializer(serializers.ModelSerializer):
    # LAZY IMPORT: Dışarıda yaparsan circular import oluyor!
    def get_stocks(self, obj):
        from .stock_serializers import StockListSerializer
        return StockListSerializer(obj.stocks.all(), many=True).data

    stocks = serializers.SerializerMethodField()

    class Meta:
        model = Index
        fields = ['id', 'name', 'stocks']
