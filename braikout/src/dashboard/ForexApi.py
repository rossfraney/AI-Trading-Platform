""" FX API wrapper """
from datetime import datetime
from decimal import Decimal
import boto3

from oandapyV20 import oandapyV20
import oandapyV20.endpoints.positions as positions
import oandapy
import v20

account_id = ''
oanda = oandapy.API(environment="practice", access_token="")
client = oandapyV20.API('')

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
dynamoTable = dynamodb.Table('trade_stats')

api = v20.Context('api-fxpractice.oanda.com', '443', token='')


def buy_order(inst, units, ticker):
    """
    Places a buy order for FX with Oanda API

    :param inst: Instrument to buy
    :param units: Units to buy
    :param ticker: Ticker representation in Dynamo DB
    """
    now = datetime.now()
    now_min = str("%s:%s.%s" % (now.hour, now.minute, now.second))
    response = api.order.market(
        account_id,
        instrument=inst,
        units=units
    )
    dynamoTable.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'min': now_min,
            'coin': ticker,
            'size': Decimal(str(float(units))),
            'pos': 'Long,'
        }
    )
    return "Response: {} ({})".format(response.status, response.reason)


def sell_order(inst):
    """
    Places an order to close positions for FX with Oanda API

    :param inst: Instrument to sell
    """
    data = {"longUnits": "ALL"}
    r = positions.PositionClose(accountID=account_id,
                                instrument=inst,
                                data=data)
    client.request(r)
    return r.response


def get_pos():
    """
    get current positions
    """
    r = positions.OpenPositions(accountID=account_id)
    client.request(r)
    return r.response
