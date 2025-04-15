# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/serializers/portfolio_serializers.py

from rest_framework import serializers
from ..models import Portfolio, PortfolioTransaction, PortfolioHolding
from decimal import Decimal

class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for user portfolios"""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'currency', 'is_default', 'user', 'created_at']


class PortfolioTransactionSerializer(serializers.ModelSerializer):
    """Serializer for portfolio transactions"""
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    
    class Meta:
        model = PortfolioTransaction
        fields = [
            'id', 'transaction_type', 'transaction_date', 'stock', 'stock_symbol', 
            'stock_name', 'quantity', 'price_per_unit', 'fees', 'notes'
        ]
        extra_kwargs = {
            'stock': {'write_only': True}
        }


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    """Serializer for portfolio holdings"""
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.SerializerMethodField()
    market_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    profit_loss_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioHolding
        fields = [
            'id', 'stock', 'stock_symbol', 'stock_name', 'quantity', 
            'average_cost', 'current_price', 'market_value', 'profit_loss',
            'profit_loss_percent', 'last_updated'
        ]
        extra_kwargs = {
            'stock': {'write_only': True}
        }
    
    def get_current_price(self, obj):
        from ..models import StockPrice
        latest_price = StockPrice.objects.filter(stock=obj.stock).order_by('-date').first()
        if latest_price:
            return float(latest_price.close)
        return None
    
    def get_market_value(self, obj):
        from ..models import StockPrice
        latest_price = StockPrice.objects.filter(stock=obj.stock).order_by('-date').first()
        if latest_price:
            return float(obj.quantity * latest_price.close)
        return None
    
    def get_profit_loss(self, obj):
        from ..models import StockPrice
        latest_price = StockPrice.objects.filter(stock=obj.stock).order_by('-date').first()
        if latest_price:
            cost_basis = obj.quantity * obj.average_cost
            market_value = obj.quantity * latest_price.close
            return float(market_value - cost_basis)
        return None
    
    def get_profit_loss_percent(self, obj):
        from ..models import StockPrice
        latest_price = StockPrice.objects.filter(stock=obj.stock).order_by('-date').first()
        if latest_price and obj.average_cost > 0:
            return float((latest_price.close - obj.average_cost) / obj.average_cost * 100)
        return None


class PortfolioCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating portfolios"""
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'currency', 'is_default']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating portfolio transactions"""
    stock_symbol = serializers.CharField(write_only=True)
    
    class Meta:
        model = PortfolioTransaction
        fields = [
            'transaction_type', 'transaction_date', 'stock_symbol',
            'quantity', 'price_per_unit', 'fees', 'notes'
        ]
    
    def validate_stock_symbol(self, value):
        from ..models import Stock
        try:
            Stock.objects.get(symbol=value)
            return value
        except Stock.DoesNotExist:
            raise serializers.ValidationError(f"Stock with symbol '{value}' not found")
    
    def validate(self, data):
        # Validate transaction type
        valid_types = dict(PortfolioTransaction.TRANSACTION_TYPES).keys()
        if data['transaction_type'] not in valid_types:
            raise serializers.ValidationError(f"Invalid transaction type. Must be one of: {', '.join(valid_types)}")
        
        # Validate quantity is positive
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        
        # Validate price is non-negative
        if data['price_per_unit'] < 0:
            raise serializers.ValidationError("Price per unit cannot be negative")
        
        # Validate fees are non-negative
        if data.get('fees', 0) < 0:
            raise serializers.ValidationError("Fees cannot be negative")
        
        # If selling, validate there's enough shares available
        if data['transaction_type'] == 'sell':
            # Note: This validation requires portfolio context, handled in the view
            pass
        
        return data