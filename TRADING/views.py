from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import get_asset_price, get_assets_details,assetsHistoryPrice
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

from .models import SearchHistory

# Vista para el Frontend (HTML)
def index(request):
    return render(request, 'TRADING/index.html')

# Vista para la API REST (JSON)
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

#Vista para los detalles de un activo 
class AssetTickerDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, ticker):
        data=get_assets_details(ticker)
        
        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(data, status=status.HTTP_200_OK)
    
class RegisterView(APIView):
    # Permitimos que cualquier persona (AllowAny) pueda acceder a esta ruta
    # porque obviamente aún no tienen token para registrarse 
    permission_classes = [AllowAny]

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
        
        # 4. Si hay algún error (ej: email ya existe), devuelve el fallo exacto
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AssetsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker, interval, period):
        data = assetsHistoryPrice(ticker, interval, period)
        
        if "error" in data:
            return Response({"detail": data["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)