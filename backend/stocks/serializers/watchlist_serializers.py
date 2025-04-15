# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/serializers/watchlist_serializers.py

from rest_framework import serializers
from ..models import Watchlist, WatchlistItem

class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for watchlists"""
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'description', 'is_default', 'created_at']