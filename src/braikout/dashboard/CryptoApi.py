""" Crypto trading API wrapper """
from decimal import Decimal
import datetime
import os
import boto3
import django
import bitstamp.client
from botocore.exceptions import ClientError
from django import shortcuts
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'braikout.settings'
django.setup()

PUBLIC_CLIENT = bitstamp.client.Public()
CUSTOMER_ID = '250960'
API_KEY = ''
SECRET = ''

DYNAMO_db = boto3.resource('dynamodb', region_name='us-east-2')
DYNAMOTABLE = DYNAMO_db.Table('trade_stats')

username = "ross"
dynamoTableAuth = DYNAMO_db.Table('auth')
try:
    response_auth = dynamoTableAuth.get_item(
        Key={
            'username': username
        }
    )
except ClientError as e:
    print(e.response['Error']['Message'])
    shortcuts.redirect('/dashboard/auth-keys')
else:
    user_auth = response_auth['Item']
    API_KEY = user_auth['cryptoapi']
    SECRET = user_auth['cryptosec']

# SECRET =

TRADING_CLIENT = bitstamp.client.Trading(
    CUSTOMER_ID, API_KEY, SECRET)


def get_volume(ticker):

    """Return volume of ticker passed as param"""

    return TRADING_CLIENT.ticker(ticker, "usd")['volume']


def get_balance(ticker):

    """Return balance of ticker passed as param"""

    return TRADING_CLIENT.account_balance(ticker, 'usd')


def get_equity():

    """ return total equity in USD"""

    equity = 0
    wallet = get_balance_eq()
    for key, val in wallet.items():
        if key != 'usd':
            equity = equity + (float(val) * float(get_prices(key, 'usd')['last']))
    equity = equity + float(get_balance("btc")["usd_balance"])
    return Decimal(str(equity))


def buy_crypto(amount, ticker):

    """Purchase cryptocurrency coin.
    Params: amount to purchase, ticker of coin to purchase
    Stores trade in Dynamo DB table"""

    now = datetime.datetime.now()
    now_min = str("%s:%s.%s" % (now.hour, now.minute, now.second))
    TRADING_CLIENT.buy_market_order(amount, ticker, 'usd')
    prices = get_prices(ticker, "usd")
    last_price = prices['last']
    equity = get_equity()

    DYNAMOTABLE.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'min': now_min,
            'coin': ticker,
            'size': Decimal(str(float(amount) * float(last_price))),
            'pos': 'Long',
            'equity': equity
        }
    )


def sell_crypto(amount, ticker):

    """Sell cryptocurrency coin.
    Params: amount to sell, ticker of coin to sell
    Stores trade in Dynamo DB table"""

    now = datetime.datetime.now()
    now_min = str("%s:%s.%s" % (now.hour, now.minute, now.second))
    TRADING_CLIENT.sell_market_order(amount, ticker, 'usd')
    prices = get_prices(ticker, "usd")
    last_price = prices['last']
    equity = get_equity()
    DYNAMOTABLE.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'min': now_min,
            'coin': ticker,
            'size': Decimal(str(float(amount) * float(last_price))),
            'pos': 'Sell',
            'equity': equity
        }
    )


def get_prices(coin, quote):

    """ Return price for the coin in param. Quote is USD by default"""

    return PUBLIC_CLIENT.ticker(coin, quote)


def get_balance_eq():

    """ Return representation of the users current wallet """

    usd_balance = get_balance("btc")["usd_balance"]
    btc_balance = get_balance("btc")["btc_balance"]
    ltc_balance = get_balance("ltc")["ltc_balance"]
    eth_balance = get_balance("eth")["eth_balance"]
    eur_balance = get_balance("eur")["eur_balance"]
    wallet = {'usd': str(round(float(usd_balance), 2)), 'btc': str(round(float(btc_balance), 2)),
              'ltc': str(round(float(ltc_balance), 2)), 'eth': str(round(float(eth_balance), 2)),
              'eur': str(round(float(eur_balance), 2))}
    return wallet
