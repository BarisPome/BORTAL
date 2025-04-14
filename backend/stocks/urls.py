from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('indices/', views.IndexListAPIView.as_view(), name='index-list'),
    path('indices/<str:name>/', views.IndexDetailAPIView.as_view(), name='index-detail'),
    path('stocks/', views.StockListAPIView.as_view(), name='stock-list'),
]