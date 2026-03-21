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
    
def get_assets_details(ticker: str) -> dict:
    try:
        asset=yf.Ticker(ticker)
        info=asset.info

        # Validar si existe el precio
        price=info.get("currentPrice") or info.get("regularMarketPrice")
        if not price:
            return {"error": "Ticker no encontrado 🔎❌"}
        
        return {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "type": info.get("quoteType", "unknown").lower(),
            "price": price,
            "currency": info.get("currency", "USD"),
            "sector": info.get("sector"),           # Solo stocks
            "industry": info.get("industry"),        # Solo stocks
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "description": info.get("longBusinessSummary"),
        }
    except Exception as e:
            return {"error": str(e)}
    

def assetsHistoryPrice(ticker :str,interval: str,period: str) -> dict:
    try:
        asset=yf.Ticker(ticker)
        hist=asset.history(interval=interval,period=period)
        if hist.empty:
            return {"error": "No hay historial de precios 🔎❌"} 
        else:
            hist = hist.reset_index()
            hist['Date'] = hist['Date'].astype(str)
            return {
                "ticker": ticker,
                "interval": interval,
                "period": period,
                "data": hist.to_dict(orient="records"),
            }
    except Exception as e:
        return {"error": str(e)}