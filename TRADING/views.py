from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import get_asset_price
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