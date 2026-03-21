from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .services import get_asset_price, get_assets_details, assetsHistoryPrice,searchAsset
from .serializers import RegisterSerializer, FavoriteSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import SearchHistory, Favorite
# Mapeamos los valores que devuelve yfinance al formato del modelo
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
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. El frontend nos tiene que enviar su refresh token en el JSON
            refresh_token = request.data["refresh"]
            
            # 2. Lo convertimos en un objeto Token de SimpleJWT
            token = RefreshToken(refresh_token)
            
            # 3. ¡Lo fulminamos! (Lo metemos en la lista negra)
            token.blacklist()
            
            return Response({"mensaje": "Sesión cerrada correctamente."}, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            # Si el token ya estaba en la lista negra o es falso, da error
            return Response({"error": "El token es inválido o ya ha expirado."}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileView(APIView):
    # Exigimos que el usuario tenga un token válido para entrar aquí
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user ya tiene los datos del usuario que hizo la petición
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ── Assets ────────────────────────────────────────────────────────────────────

class AssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        data = get_asset_price(ticker)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        # Mapeo de quoteType → asset_type del modelo
        TYPE_MAP = {
        "equity": "stock",
        "cryptocurrency": "crypto",
        "etf": "etf"
        }

        asset_type = TYPE_MAP.get(data["type"], "stock")

        # Guardar historial
        SearchHistory.objects.create(
            user=request.user,
            ticker=ticker,
            asset_type=asset_type,
            price_at_query=data["price"]
        )

        return Response(data, status=status.HTTP_200_OK)


class AssetTickerDetail(APIView):
    permission_classes = [IsAuthenticated]

    # ⚠️ BUG CORREGIDO: antes se llamaba get_ticker_detail → DRF nunca lo ejecutaba
    def get(self, request, ticker):
        data = get_assets_details(ticker)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)

class AssetsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):  # ← solo ticker
        period = request.query_params.get("period", "1mo")
        interval = request.query_params.get("interval", "1d")
        data = assetsHistoryPrice(ticker, interval, period)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)
        
class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        data = searchAsset(query)

        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)
    
# ── Favoritos ─────────────────────────────────────────────────────────────────

class FavoriteListCreateView(APIView):
    """
    GET  /api/v1/favorites/  → Lista los favoritos del usuario
    POST /api/v1/favorites/  → Añade un activo a favoritos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).order_by('-added_at')
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 1. Le pasamos los datos del frontend al serializador
        serializer = RegisterSerializer(data=request.data)
        
        # 2. Comprobamos si los datos son válidos (ej: que el email tenga el @, que no esté repetido, etc.)
        if serializer.is_valid():
            # 3. Guarda el usuario en la base de datos ejecutando el método 'create' de arriba
            serializer.save()
            return Response(
                {"mensaje": "Usuario creado con éxito. ¡Ya puedes iniciar sesión!"}, 
                status=status.HTTP_201_CREATED
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritePricesView(APIView):
    """
    GET /api/v1/favorites/prices/  → Precios actuales de todos los favoritos
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
                # Si un ticker falla no rompemos el endpoint entero
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

        return Response(data, status=status.HTTP_200_OK)