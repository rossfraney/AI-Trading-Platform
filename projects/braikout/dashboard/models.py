""" Coin and User models"""
from django.db import models


class CoinPrices(models.Model):
    """ Coin model"""
    ticker = models.CharField(max_length=5)  # 3 is probably enough
    name = models.CharField(max_length=15, default=False)
    current_price = models.FloatField(max_length=10)  # not sure on number here
    coin_logo = models.CharField(max_length=1000)
    predictions = models.FloatField(max_length=10)
    sentiment_score = models.FloatField(max_length=10)
    trend = models.CharField(max_length=15, default=False)

    def __str__(self):
        return self.ticker + ' - ' + str(self.current_price)

    is_favorite = models.BooleanField(default=False)


class UserProfile(models.Model):
    """ User model """
    name = models.CharField(max_length=15, default=False)
    usd_balance = models.FloatField(max_length=10)
    btc_balance = models.FloatField(max_length=10)
    ltc_balance = models.FloatField(max_length=10)
    eth_balance = models.FloatField(max_length=10)
    eur_balance = models.FloatField(max_length=10)
    balance = models.FloatField(max_length=10)
