from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .services import get_asset_price, get_assets_details, assetsHistoryPrice, searchAsset
from .serializers import RegisterSerializer, FavoriteSerializer, UserProfileSerializer
from .models import SearchHistory, Favorite

TYPE_MAP = {
    "equity": "stock",
    "cryptocurrency": "crypto",
    "etf": "etf"
}

# ── Frontend ──────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'TRADING/index.html')


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Usuario creado con éxito. ¡Ya puedes iniciar sesión!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Assets ────────────────────────────────────────────────────────────────────

class AssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        data = get_asset_price(ticker)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        asset_type = TYPE_MAP.get(data["type"], "stock")

        SearchHistory.objects.create(
            user=request.user,
            ticker=ticker,
            asset_type=asset_type,
            price_at_query=data["price"]
        )

        return Response(data, status=status.HTTP_200_OK)


class AssetTickerDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        data = get_assets_details(ticker)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)


class AssetHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        period = request.query_params.get("period", "1mo")
        interval = request.query_params.get("interval", "1d")
        data = assetsHistoryPrice(ticker, period, interval)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        data = searchAsset(query)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)


# ── Favoritos ─────────────────────────────────────────────────────────────────

class FavoriteListCreateView(APIView):
    """
    GET /api/v1/favorites/ → Lista los favoritos del usuario
    POST /api/v1/favorites/ → Añade un activo a favoritos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).order_by('-added_at')
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        ticker = request.data.get('ticker', '').upper().strip()

        if not ticker:
            return Response(
                {'error': 'El campo ticker es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = get_asset_price(ticker)
        if "error" in data:
            return Response(
                {'error': f'Ticker {ticker} no encontrado en Yahoo Finance.'},
                status=status.HTTP_404_NOT_FOUND
            )

        asset_type = TYPE_MAP.get(data["type"], "stock")

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            ticker=ticker,
            asset_type=asset_type,
        )

        if not created:
            return Response(
                {'error': f'{ticker} ya está en tus favoritos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            favorite = Favorite.objects.get(pk=pk, user=request.user)
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'Favorito no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritePricesView(APIView):
    """
    GET /api/v1/favorites/prices/ → Precios actuales de todos los favoritos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)

        if not favorites.exists():
            return Response([])

        prices = []
        for fav in favorites:
            data = get_asset_price(fav.ticker)
            if "error" in data:
                prices.append({
                    'id': fav.id,
                    'ticker': fav.ticker,
                    'asset_type': fav.asset_type,
                    'error': 'No se pudo obtener el precio.'
                })
            else:
                prices.append({
                    'id': fav.id,
                    'asset_type': fav.asset_type,
                    **data
                })

        return Response(prices)  # ← devuelve prices, no data

# ── Auth adicional ─────────────────────────────────────────────────────────────

class UserProfileView(APIView):
    """
    GET /api/v1/auth/me/  → Devuelve los datos del usuario autenticado
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/  → Invalida el refresh token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "El campo refresh es obligatorio."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"mensaje": "Sesión cerrada correctamente."},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Token inválido o ya expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )