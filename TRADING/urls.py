from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AssetDetailView,AssetTickerDetail,AssetsHistoryView,SearchView

urlpatterns = [
# Autenticación JWT API
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Activos Financieros
    #debe ir de primera porque sino no llega al details
    path('assets/search/', SearchView.as_view(), name='search'),
    path('assets/<str:ticker>/detail/', AssetTickerDetail.as_view(), name='asset_ticker_detail'),
    path('assets/<str:ticker>/history/', AssetsHistoryView.as_view(), name='asset_history'),
    #Al final la mas generica
    path('assets/<str:ticker>/', AssetDetailView.as_view(), name='asset_detail'),
]
