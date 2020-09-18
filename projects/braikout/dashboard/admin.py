""" Admin module """
from django.contrib import admin
from .models import CoinPrices

admin.site.register(CoinPrices)
