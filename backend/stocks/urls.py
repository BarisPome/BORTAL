from django.urls import path
from .api import (
    IndexListAPIView, 
    IndexDetailAPIView, 
    StockListAPIView, 
    StockDetailAPIView
)

urlpatterns = [
    path('indices/', IndexListAPIView.as_view(), name='index-list'),
    path('indices/<str:name>/', IndexDetailAPIView.as_view(), name='index-detail'),
    path('stocks/', StockListAPIView.as_view(), name='stock-list'),
    path('stocks/<str:symbol>/detail/', StockDetailAPIView.as_view(), name='stock-detail'),
]