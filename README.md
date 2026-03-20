# Investing API

API REST desarrollada con Django para consultar precios de acciones, criptomonedas y ETFs en tiempo real usando Yahoo Finance.

## Tecnologías usadas

- Django 6.0
- Django REST Framework
- SimpleJWT (autenticación)
- yfinance (datos financieros)
- SQLite

## Instalación

1. Clona el repositorio
2. Instala las dependencias con `uv sync`
3. Aplica las migraciones con `uv run manage.py migrate`
4. Crea un usuario con `uv run manage.py createsuperuser`
5. Arranca el servidor con `uv run manage.py runserver`

## Autenticación

La API usa tokens JWT. Primero haz login para obtener tu token:

- **POST** `/api/v1/auth/login/` → devuelve `access` y `refresh`
- En cada petición añade el header: `Authorization: Bearer <token>`
- **POST** `/api/v1/auth/refresh/` → renueva el token cuando caduca

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Iniciar sesión |
| POST | `/api/v1/auth/register/` | Registrar usuario |
| GET | `/api/v1/assets/{ticker}/` | Precio actual |
| GET | `/api/v1/assets/{ticker}/details/` | Info completa |
| GET | `/api/v1/assets/{ticker}/history/` | Historial de precios |
| GET | `/api/v1/assets/search/?q={query}` | Buscar activos |

## Ejemplos

Precio de Apple:
```
GET /api/v1/assets/AAPL/
```

Bitcoin:
```
GET /api/v1/assets/BTC-USD/
```

Historial del último mes:
```
GET /api/v1/assets/AAPL/history/?period=1mo&interval=1d
```

Buscar activos:
```
GET /api/v1/assets/search/?q=tesla
```

## Equipo

Proyecto desarrollado por 4 integrantes como práctica del módulo DAW.