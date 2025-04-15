from rest_framework import serializers
from ..models import Stock, StockPrice, StockFundamental, TechnicalIndicator
from .sector_serializers import SectorSerializer
from .index_serializers import IndexSerializer  # bu yeterli

class StockListSerializer(serializers.ModelSerializer):
    sector_name = serializers.CharField(source='sector.display_name', read_only=True, allow_null=True)

    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'sector_name']


class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume']


class StockDetailSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(read_only=True)
    indices = IndexSerializer(many=True, read_only=True)
    latest_price = serializers.SerializerMethodField()
    price_change = serializers.SerializerMethodField()
    price_change_percent = serializers.SerializerMethodField()
    fundamentals = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'symbol', 'name', 'description', 'sector', 'country',
            'exchange', 'currency', 'indices', 'latest_price',
            'price_change', 'price_change_percent', 'fundamentals'
        ]
    
    def get_latest_price(self, obj):
        latest_price = obj.prices.order_by('-date').first()
        if latest_price:
            return StockPriceSerializer(latest_price).data
        return None

    def get_price_change(self, obj):
        prices = obj.prices.order_by('-date')[:2]
        if len(prices) >= 2:
            return float(prices[0].close - prices[1].close)
        return None

    def get_price_change_percent(self, obj):
        prices = obj.prices.order_by('-date')[:2]
        if len(prices) >= 2 and prices[1].close > 0:
            return float((prices[0].close - prices[1].close) / prices[1].close * 100)
        return None

    def get_fundamentals(self, obj):
        fundamentals = obj.fundamentals.order_by('-date').first()
        if fundamentals:
            return {
                'date': fundamentals.date,
                'market_cap': fundamentals.market_cap,
                'pe_ratio': fundamentals.pe_ratio,
                'eps': fundamentals.eps,
                'dividend_yield': fundamentals.dividend_yield,
                'price_to_book': fundamentals.price_to_book,
                'roe': fundamentals.roe,
                'profit_margin': fundamentals.profit_margin
            }
        return None


class StockTechnicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalIndicator
        fields = '__all__'
