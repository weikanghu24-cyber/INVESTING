from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AssetDetailView

urlpatterns = [
# Autenticación JWT API
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Activos Financieros
    path('assets/<str:ticker>/', AssetDetailView.as_view(), name='asset_detail'),
    
]
