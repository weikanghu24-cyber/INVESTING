import yfinance as yf
from django.core.cache import cache

def get_asset_price(ticker: str) -> dict:
    cache_key = f'price_{ticker}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
        
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        
        # Validar si existe el precio
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not price:
            return {"error": "Ticker no encontrado"}

        data = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "type": info.get("quoteType", "unknown").lower(),
            "price": price,
            "currency": info.get("currency", "USD"),
            "change_pct": info.get("regularMarketChangePercent", 0),
            "volume": info.get("regularMarketVolume", 0),
        }
        
        cache.set(cache_key, data, timeout=60)
        return data
        
    except Exception as e:
        return {"error": str(e)}