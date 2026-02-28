from django.db import models
from django.contrib.auth.models import User

class Favorite(models.Model):
    ASSET_TYPES = [('stock', 'Stock'), ('crypto', 'Crypto'), ('etf', 'ETF')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticker')

class SearchHistory(models.Model):
    ASSET_TYPES = [('stock', 'Stock'), ('crypto', 'Crypto'), ('etf', 'ETF')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    price_at_query = models.DecimalField(max_digits=12, decimal_places=4)
    queried_at = models.DateTimeField(auto_now_add=True)