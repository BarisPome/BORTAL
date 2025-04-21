# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/urls.py

from django.urls import path
from .api.sector_api import SectorListAPIView
from .api.index_api import IndexListAPIView
from .api.stock_api import (
    StockListAPIView, StockDetailAPIView,
    StockPriceAPIView, StockTechnicalAPIView
)
from .api.news_api import StockNewsAPIView
from .api.watchlist_api import WatchlistAPIView, WatchlistItemAPIView
from .api.portfolio_api import (
    PortfolioListAPIView, PortfolioDetailAPIView, 
    PortfolioTransactionAPIView, PortfolioPerformanceAPIView
)
from .api.dashboard_api import DashboardAPIView

from rest_framework_simplejwt.views import TokenRefreshView
from .api.auth_views import LoginView, RegisterView, LogoutView, UserProfileView



urlpatterns = [
    # Stock Market Data
    path('sectors/', SectorListAPIView.as_view(), name='sector-list'),
    path('indices/', IndexListAPIView.as_view(), name='index-list'),
    path('stocks/', StockListAPIView.as_view(), name='stock-list'),
    path('stocks/<str:symbol>/', StockDetailAPIView.as_view(), name='stock-detail'),
    path('stocks/<str:symbol>/technical/', StockTechnicalAPIView.as_view(), name='stock-technical'),
    
    # News
    path('news/', StockNewsAPIView.as_view(), name='news-list'),
    path('stocks/<str:symbol>/news/', StockNewsAPIView.as_view(), name='stock-news'),
    
    # Watchlists
    path('watchlists/', WatchlistAPIView.as_view(), name='watchlist-list'),
    path('watchlists/<uuid:watchlist_id>/', WatchlistAPIView.as_view(), name='watchlist-detail'),
    path('watchlists/<uuid:watchlist_id>/stocks/', WatchlistItemAPIView.as_view(), name='watchlist-add-stock'),
    path('watchlists/<uuid:watchlist_id>/stocks/<str:symbol>/', WatchlistItemAPIView.as_view(), name='watchlist-item-detail'),

    # Portfolios
    path('portfolios/', PortfolioListAPIView.as_view(), name='portfolio-list'),
    path('portfolios/<uuid:portfolio_id>/', PortfolioDetailAPIView.as_view(), name='portfolio-detail'),
    path('portfolios/<uuid:portfolio_id>/transactions/', PortfolioTransactionAPIView.as_view(), name='portfolio-transactions'),
    path('portfolios/<uuid:portfolio_id>/transactions/<uuid:transaction_id>/', PortfolioTransactionAPIView.as_view(), name='portfolio-transaction-detail'),
    path('portfolios/<uuid:portfolio_id>/performance/', PortfolioPerformanceAPIView.as_view(), name='portfolio-performance'),
    
    # Dashboard
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
]