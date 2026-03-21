from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    AssetDetailView,
    AssetTickerDetail,
    AssetHistoryView,        # ← corregido, sin 's'
    RegisterView,
    LogoutView,
    UserProfileView,
    SearchView,
    FavoriteListCreateView,
    FavoriteDeleteView,
    FavoritePricesView,
)

urlpatterns = [
    # Auth
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', UserProfileView.as_view(), name='user_profile'),

    # Assets — las rutas específicas ANTES de la genérica <ticker>
    path('assets/search/', SearchView.as_view(), name='search'),
    path('assets/<str:ticker>/detail/', AssetTickerDetail.as_view(), name='asset_ticker_detail'),
    path('assets/<str:ticker>/history/', AssetHistoryView.as_view(), name='asset_history'),
    path('assets/<str:ticker>/', AssetDetailView.as_view(), name='asset_detail'),

    # Favoritos — prices/ ANTES de <int:pk>/
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/prices/', FavoritePricesView.as_view(), name='favorite-prices'),
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
]