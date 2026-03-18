# Importamos el sistema de modelos de Django (para crear tablas en la base de datos)
from django.db import models

# Importamos el modelo base de usuario de Django
from django.contrib.auth.models import AbstractUser
from configuracion import settings


# -------------------------------
# MODELO DE USUARIO PERSONALIZADO
# -------------------------------
class User(AbstractUser):
    """
    Creamos un modelo de usuario propio.
    Hereda de AbstractUser para mantener todo el sistema de
    autenticación de Django (login, permisos, admin, etc.).
    """

    # Email único para cada usuario
    email = models.EmailField(unique=True)

    # Foto de perfil del usuario
    # Se guardará en la carpeta media/avatars/
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Fecha en la que se creó el usuario
    # Se asigna automáticamente al crear el registro
    created_at = models.DateTimeField(auto_now_add=True)

    # Usamos el email como campo principal para iniciar sesión
    USERNAME_FIELD = 'email'

    # Campos obligatorios al crear un superusuario desde consola
    REQUIRED_FIELDS = ['username']

    class Meta:
        # Nombre mostrado en el panel admin
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # Cómo se mostrará el usuario cuando se imprima
    def __str__(self):
        return self.email


# -------------------------------
# TIPOS DE ACTIVOS DISPONIBLES
# -------------------------------
ASSET_TYPES = [
    ('stock', 'Stock'),
    ('crypto', 'Crypto'),
    ('etf', 'ETF')
]


# -------------------------------
# MODELO DE FAVORITOS
# -------------------------------
class Favorite(models.Model):
    """
    Guarda los activos que un usuario ha marcado como favoritos.
    """

    # Relación con el usuario
    # Si el usuario se elimina, también se eliminan sus favoritos
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    # Símbolo del activo (ej: BTC, AAPL, TSLA)
    ticker = models.CharField(max_length=20, db_index=True)

    # Tipo de activo (stock, crypto, etf)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)

    # Fecha en que se añadió el favorito
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evita que un usuario guarde el mismo activo dos veces
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ticker', 'asset_type'],
                name='unique_user_asset'
            )
        ]

    # Cómo se mostrará el favorito en el admin o al imprimirlo
    def __str__(self):
        return f"{self.user} - {self.ticker} ({self.asset_type})"


# -------------------------------
# MODELO DE HISTORIAL DE BÚSQUEDAS
# -------------------------------
class SearchHistory(models.Model):
    """
    Guarda cada búsqueda que hace un usuario.
    Permite mostrar historial o estadísticas.
    """

    # Usuario que realizó la búsqueda
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="search_history"
    )

    # Activo que buscó (ticker)
    ticker = models.CharField(max_length=20, db_index=True)

    # Tipo de activo
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)

    # Precio del activo en el momento de la búsqueda
    price_at_query = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    # Fecha en que se hizo la búsqueda
    queried_at = models.DateTimeField(auto_now_add=True)