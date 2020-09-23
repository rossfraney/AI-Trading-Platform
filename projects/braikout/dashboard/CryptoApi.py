import datetime
import os
import boto3
import django
import bitstamp.client

from decimal import Decimal
from botocore.exceptions import ClientError
from django import shortcuts
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'braikout.settings'
django.setup()


class CryptoApi:
    
    def __init__(self):
        self.public_client = bitstamp.client.Public()
        self.customer_id = "250960"
        self.api_key = ""
        self.secret = ""
        self.dynamo_db = boto3.resource('dynamodb', region_name='us-east-2')
        self.dynamo_table = self.dynamo_db.Table('trade_stats')
        self.username = "ross"
        self.trading_client = self._get_trading_authentication()

    def get_volume(self, ticker):
        """Return volume of ticker passed as param"""
        return self.trading_client.ticker(ticker, "usd")['volume']

    def get_balance(self, ticker):
        """Return balance of ticker passed as param"""
        return self.trading_client.account_balance(ticker, 'usd')

    def get_equity(self):
        """ return total equity in USD"""
        equity = 0
        wallet = self.get_balance_eq()
        for key, val in wallet.items():
            if key != 'usd':
                equity += (float(val) * float(get_prices(key, 'usd')['last']))
        equity = equity + float(self.get_balance("btc")["usd_balance"])
        return Decimal(str(equity))

    def buy_crypto(self, amount, ticker):
        """Purchase cryptocurrency coin.
        Params: amount to purchase, ticker of coin to purchase
        Stores trade in Dynamo DB table"""
        self.trading_client.buy_market_order(amount, ticker, 'usd')
        self._update_db(ticker, amount, 'Long')

    def sell_crypto(self, amount, ticker):
        """Sell cryptocurrency coin.
        Params: amount to sell, ticker of coin to sell
        Stores trade in Dynamo DB table"""
        self.trading_client.sell_market_order(amount, ticker, 'usd')
        self._update_db(ticker, amount, 'Sell')

    def get_prices(self, coin, quote):
        """ Return price for the coin in param. Quote is USD by default"""

        return self.public_client.ticker(coin, quote)

    def _update_db(self, ticker, amount, position_type):
        now = datetime.datetime.now()
        now_min = str("%s:%s.%s" % (now.hour, now.minute, now.second))

        prices = self.get_prices(ticker, "usd")
        last_price = prices['last']
        equity = self.get_equity()

        self.dynamo_table.put_item(
            Item={
                'date': now.strftime("%Y-%m-%d"),
                'min': now_min,
                'coin': ticker,
                'size': Decimal(str(float(amount) * float(last_price))),
                'pos': position_type,
                'equity': equity
            }
        )

    def _get_trading_authentication(self):
        auth_table = self.dynamo_table.Table('auth')
        try:
            response_auth = auth_table.get_item(
                Key={
                    'username': self.username
                }
            )
        except ClientError as e:
            shortcuts.redirect('/dashboard/auth-keys')
        else:
            user_auth = response_auth['Item']
            self.api_key = user_auth['cryptoapi']
            self.secret = user_auth['cryptosec']
        return bitstamp.client.Trading(self.customer_id, self.api_key, self.secret)

    def get_balance_eq(self):
        """ Return representation of the users current wallet """
        usd_balance = self.get_balance("btc")["usd_balance"]
        btc_balance = self.get_balance("btc")["btc_balance"]
        ltc_balance = self.get_balance("ltc")["ltc_balance"]
        eth_balance = self.get_balance("eth")["eth_balance"]
        eur_balance = self.get_balance("eur")["eur_balance"]
        return {'usd': str(round(float(usd_balance), 2)),
                'btc': str(round(float(btc_balance), 2)),
                'ltc': str(round(float(ltc_balance), 2)),
                'eth': str(round(float(eth_balance), 2)),
                'eur': str(round(float(eur_balance), 2))}

