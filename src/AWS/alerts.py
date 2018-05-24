""" Module to check for user alert conditions and return """ 
import datetime
import json
import boto3
from botocore.exceptions import ClientError
import bitstamp.client
import decimal

from pyfcm import FCMNotification
PUBLIC_CLIENT = bitstamp.client.Public()
CUSTOMER_ID = '250960'
API_KEY = ''
# API_KEY =
SECRET = ''

DYNAMO_db = boto3.resource('dynamodb', region_name='us-east-2')
DYNAMOTABLE = DYNAMO_db.Table('trade_stats')
DYNAMOTABLE_WALLET = DYNAMO_db.Table('wallet')


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

TRADING_CLIENT = bitstamp.client.Trading(
CUSTOMER_ID, API_KEY, SECRET)

def get_balance(ticker):

    """Return balance of ticker passed as param"""

    return TRADING_CLIENT.account_balance(ticker, 'usd')


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


def check_for_break(ticker):
    """ Checks for break in the current price in comparisont to users alerts """ 
    public_client = bitstamp.client.Public()
    return float(public_client.ticker(ticker.lower(), 'usd')['last'])


def get_equity():

    """ return total equity in USD"""

    equity = 0
    wallet = get_balance_eq()
    for key, val in wallet.items():
        if key != 'usd':
            equity = equity + (float(val) * float(get_prices(key, 'usd')['last']))
    equity = equity + float(get_balance("btc")["usd_balance"])
    return decimal.Decimal(str(equity))


def notify():
    """ Notifications to the App via firebase server """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('alerts')
    val = " "
    try:
        response = dynamoTables.get_item(
            Key={
                'coin_id': "tokenId"
            }
        )
        response_BTC = dynamoTables.get_item(
            Key={
                'coin_id': "BTC"
            }
        )
        response_LTC = dynamoTables.get_item(
            Key={
                'coin_id': "LTC"
            }
        )
        response_ETH = dynamoTables.get_item(
            Key={
                'coin_id': "ETH"
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        item_btc = response_BTC['Item']
        item_eth = response_ETH['Item']
        item_ltc = response_LTC['Item']
        print("Get Item Succeeded")
        results = (json.dumps(item, indent=4, cls=DecimalEncoder)) 
        results_BTC = (json.dumps(item_btc, indent=4, cls=DecimalEncoder))
        results_ETH = (json.dumps(item_eth, indent=4, cls=DecimalEncoder))
        results_LTC = (json.dumps(item_ltc, indent=4, cls=DecimalEncoder)) 
        jsondata_charts = json.loads(results)
        jsondata_btc = json.loads(results_BTC)
        jsondata_eth = json.loads(results_ETH)
        jsondata_ltc = json.loads(results_LTC)
        token = jsondata_charts['token']
        items = [jsondata_btc, jsondata_ltc, jsondata_eth]
        for i in items:
            ticker = i['coin_id']
            if i['alert_below'] > check_for_break(ticker) and i['alert_below'] != 0:
                print("ALERT BELOW TRIGGERED")
                
                #For Demo / Grading purposes - Change to settings variable 
   
                push_service = FCMNotification(api_key="AAAAHsWsHB4:APA91bGfadwyPWvdbEZK7fAnYv-v2Z7zUxlQKi3nKA1ZGxGNx4hozTWfkMvyFcinayfcym2VG1pdRXDEHG5xUItUAKHmltZSVsvpDxafZqt8zeK9f6KGxdFVuESeZuHCv6bloCU0N-3s")
                registration_id = token
                message_title = ticker + " Price Reached"
                message_body = "Price Alert Triggered: " + ticker + " is below trigger price."
                result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
                dynamoTables.put_item(
                        Item = {
                            'coin_id': ticker,
                            'alert_above': 0,
                            'alert_below': 0
                        }
                    )
                return result
            if i['alert_above'] < check_for_break(ticker) and i['alert_above'] != 0:
                print("ALERT ABOVE TRIGGERED")
                print(token)
                
                 #For Demo / Grading purposes - Change to settings variable 
                push_service = FCMNotification(api_key="AAAAHsWsHB4:APA91bGfadwyPWvdbEZK7fAnYv-v2Z7zUxlQKi3nKA1ZGxGNx4hozTWfkMvyFcinayfcym2VG1pdRXDEHG5xUItUAKHmltZSVsvpDxafZqt8zeK9f6KGxdFVuESeZuHCv6bloCU0N-3s")
                registration_id = token
                message_title = ticker + " Price Reached"
                message_body = "Price Alert Triggered: " + ticker + " is above trigger price."
                result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
                dynamoTables.put_item(
                        Item = {
                            'coin_id': ticker,
                            'alert_above': 0,
                            'alert_below': 0
                        }
                    )
                return result
        

class DecimalEncoder(json.JSONEncoder):
    """ Helper class to convert a DynamoDB item to JSON """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
   

def get_prices(coin, quote):

    """ Return price for the coin in param. Quote is USD by default"""

    return PUBLIC_CLIENT.ticker(coin, quote)


def buy_crypto(ticker, amount):
    """Purchase cryptocurrency coin.
    Params: amount to purchase, ticker of coin to purchase
    Stores trade in Dynamo DB table"""
    if amount == "0":
        return

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
            'size': decimal.Decimal(str(float(amount) * float(last_price))),
            'pos': 'Long',
            'equity': equity
        }
    )


def sell_crypto(ticker, amount):
    """Sell cryptocurrency coin.
    Params: amount to sell, ticker of coin to sell
    Stores trade in Dynamo DB table"""

    if amount == "0":
        return

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
            'size': decimal.Decimal(str(float(amount) * float(last_price))),
            'pos': 'Sell',
            'equity': equity
        }
    )


def check_for_order():
    """ Checks to see if the user has placed any orders from the mobile device """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('orders')
    val = " "
    try:
        response_BTC = dynamoTables.get_item(
            Key={
                'coin_id': "btc"
            }
        )
        response_LTC = dynamoTables.get_item(
            Key={
                'coin_id': "ltc"
            }
        )
        response_ETH = dynamoTables.get_item(
            Key={
                'coin_id': "eth"
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        jsondata_btc = []
        jsondata_eth = []
        jsondata_ltc = []
        print(len(response_BTC))
        if len(response_BTC) > 1:
            item_btc = response_BTC['Item']
            results_BTC = (json.dumps(item_btc, indent=4, cls=DecimalEncoder))
            jsondata_btc = json.loads(results_BTC)
        if len(response_ETH) > 1:
            item_eth = response_ETH['Item']
            results_ETH = (json.dumps(item_eth, indent=4, cls=DecimalEncoder))
            jsondata_eth = json.loads(results_ETH)
        if len(response_LTC) > 1:
            item_ltc = response_LTC['Item']
            results_LTC = (json.dumps(item_ltc, indent=4, cls=DecimalEncoder)) 
            jsondata_ltc = json.loads(results_LTC)
        
        items = [jsondata_btc, jsondata_ltc, jsondata_eth]
        for i in items:
            if len(i) > 1:
                ticker = i['coin_id']
                if i['type'] == "Buy":
                    print("Buy Triggered")
                    dynamoTables.delete_item(
                        Key = {
                            'coin_id': ticker,
                        }
                    )
                    buy_crypto(ticker, i['amt'])
                    wallet = get_balance_eq()
                    for key, val in wallet.items():
                        DYNAMOTABLE_WALLET.put_item(
                            Item={
                            'coin_id': key,
                            'amount':val
                            })
                if i['type'] == "Sell":
                    print("Sell Triggered")
                    dynamoTables.delete_item(
                        Key = {
                            'coin_id': ticker,
                        }
                    )
                    sell_crypto(ticker, i['amt'])
                    wallet = get_balance_eq()
                    for key, val in wallet.items():
                        DYNAMOTABLE_WALLET.put_item(
                            Item={
                            'coin_id': key,
                            'amount':val
                            })


def main():
    """ Main """ 

    notify()
    check_for_order()

if __name__ == '__main__':
    main()
