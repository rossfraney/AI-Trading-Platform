""" FX API wrapper """
from datetime import datetime
import boto3
from decimal import Decimal
from oandapyV20 import oandapyV20
import oandapyV20.endpoints.positions as positions

import oandapy

import v20
account_id = '101-004-8286259-001'
oanda = oandapy.API(
    environment="practice",
    access_token="8b5e8381818c621dc3b47f742c0e33b8-c04c9c6a3a7f5a066dbec1da5b0de23d")
client = oandapyV20.API(
    '8b5e8381818c621dc3b47f742c0e33b8-c04c9c6a3a7f5a066dbec1da5b0de23d'
)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
dynamoTable = dynamodb.Table('trade_stats')

api = v20.Context(
    'api-fxpractice.oanda.com',
    '443',
    token='8b5e8381818c621dc3b47f742c0e33b8-c04c9c6a3a7f5a066dbec1da5b0de23d')


def buy_order(inst, units, ticker):
    """ Places a buy order for FX with Oanda API """
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
    print("Response: {} ({})".format(response.status, response.reason))


def sell_order(inst):
    """ Places an order to close positions for FX with Oanda API """
    data = {"longUnits" : "ALL"}
    r = positions.PositionClose(accountID=account_id,
                                instrument=inst,
                                data=data)
    client.request(r)
    print(r.response)


def get_pos():
    """ get current position """
    r = positions.OpenPositions(accountID=account_id)
    client.request(r)
    return r.response
