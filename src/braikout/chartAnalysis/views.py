import datetime
import json

import boto3 as boto3
from botocore.exceptions import ClientError
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from dashboard.models import CoinPrices
from chartAnalysis import chartTA
from dashboard.views import DecimalEncoder
from dashboard import CryptoApi as crypto

coinlogo = ""

class LtcView(View):
    global coin_support, coin_resi, coin_trend, modal
    all_coins = CoinPrices.objects.all()
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
    dynamoTables = dynamodb.Table('crypto_predictions')
    global coinlogo
    for c in all_coins:
        if c.ticker == 'LTC':
            coinlogo = c.coin_logo

    #coin_id_tag = coin.ticker.lower()
    # coin_trend = ""
    # coin_resistance = ""
    # coin_support = ""
    now = datetime.datetime.now()
    try:
        response_charts = dynamoTables.get_item(
            Key={
                'coin_id': 'ltc'
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(response_charts)
        item2 = response_charts['Item']
        print("Get Item Succeeded")
        lol_charts = (json.dumps(item2, indent= 4, cls=DecimalEncoder))
        jsondata_charts = json.loads(lol_charts)
        coin_trend = str(jsondata_charts['trend']).upper()
        coin_resi = str(jsondata_charts['resi']).upper()
        coin_support = str(jsondata_charts['support']).upper()

    if coin_trend == 'BEAR':
        modal = "Support at " + str(coin_support) + " has been broken downward (bearish). Possible sell indication. " \
                                                     "Would you like alerts for these breaks in future? "
    else:
        if coin_trend == 'BULL':
            modal = "Resistance at " + str(coin_resi) + " has been broken upward (bullish). Possible long indication. " \
                                                    "Would you like alerts for these breaks in future? "
        else:
                modal = "LTC is in a tightening trend. This is considered a no trade zone until a break is realized. " \
                "Click the Alerts tab to be notified when a break occurs. "

    context = {'all_coins': all_coins, 'coin_trend':coin_trend, 'coin_resistance':coin_resi, 'coin_support':coin_support,
               'coin_modal': modal, 'coin_logo':coinlogo}

    def get(self, request, *args, **kwargs):
        return render(request, 'chartAnalysis/ltc_charts.html', self.context)


#BTC
class BtcView(View):
    global coin_support, coin_resi, coin_trend, modal
    all_coins = CoinPrices.objects.all()
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
    dynamoTables = dynamodb.Table('crypto_predictions')
    global coinlogo
    for c in all_coins:
        if c.ticker == 'BTC':
            coinlogo = c.coin_logo
    now = datetime.datetime.now()
    try:
        response_charts = dynamoTables.get_item(
            Key={
                'coin_id': 'btc'
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item2 = response_charts['Item']
        lol_charts = (json.dumps(item2, indent= 4, cls=DecimalEncoder))
        jsondata_charts = json.loads(lol_charts)
        coin_trend = str(jsondata_charts['trend']).upper()
        coin_resi = str(jsondata_charts['resi']).upper()
        coin_support = str(jsondata_charts['support']).upper()

    if coin_trend == 'Bearish':
        modal = "Support at " + str(coin_support) + " has been broken downward (bearish). Possible sell indication. " \
                                                    "Would you like alerts for these breaks in future? "
    else:
        if coin_trend == 'Bullish':
            modal = "Resistance at " + str(coin_resi) + " has been broken upward (bullish). Possible long indication. " \
                                                        "Would you like alerts for these breaks in future? "
        else:
            modal = "BTC is in a tightening trend. This is considered a no trade zone until a break is realized. " \
                    "Click the Alerts tab to be notified when a break occurs.  "

    context = {'all_coins': all_coins, 'coin_trend':coin_trend, 'coin_resistance':coin_resi, 'coin_support':coin_support,
               'coin_modal': modal, 'coin_logo': coinlogo}

    def get(self, request, *args, **kwargs):
        return render(request, 'chartAnalysis/btc_charts.html', self.context)

class EthView(View):
    global coin_support, coin_resi, coin_trend, modal
    all_coins = CoinPrices.objects.all()
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
    dynamoTables = dynamodb.Table('crypto_predictions')
    global coinlogo
    for c in all_coins:
        if c.ticker == 'ETH':
            coinlogo = c.coin_logo
    #coin_id_tag = coin.ticker.lower()
    # coin_trend = ""
    # coin_resistance = ""
    # coin_support = ""
    now = datetime.datetime.now()
    try:
        response_charts = dynamoTables.get_item(
            Key={
                'coin_id': 'eth'
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(response_charts)
        item2 = response_charts['Item']
        print("Get Item Succeeded")
        lol_charts = (json.dumps(item2, indent= 4, cls=DecimalEncoder))################################
        jsondata_charts = json.loads(lol_charts)
        coin_trend = str(jsondata_charts['trend']).upper()
        coin_resi = str(jsondata_charts['resi']).upper()
        coin_support = str(jsondata_charts['support']).upper()

    if coin_trend == 'BEAR':
        modal = "Support at " + str(coin_support) + " has been broken downward (bearish). Possible sell indication. " \
                                                    "Would you like alerts for these breaks in future? "
    else:
        if coin_trend == 'BULL':
            modal = "Resistance at " + str(coin_resi) + " has been broken upward (bullish). Possible long indication. " \
                                                        "Would you like alerts for these breaks in future? "
        else:
            modal = "ETH is in a tightening trend. This is considered a no trade zone until a break is realized. " \
                    "Click the Alerts tab to be notified when a break occurs.  "

    context = {'all_coins': all_coins, 'coin_trend':coin_trend, 'coin_resistance':coin_resi, 'coin_support':coin_support,
               'coin_modal': modal, 'coin_logo':coinlogo}

    def get(self, request, *args, **kwargs):
        return render(request, 'chartAnalysis/eth_charts.html', self.context)


class ChartData(APIView):
    all_coins = CoinPrices.objects.all()
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
        default_items = []
        ltc_chart = chartTA.get_ltc_chart()
        btc_chart = chartTA.get_btc_chart()
        eth_chart = chartTA.get_eth_chart()
        print(type(ltc_chart))
        for c in self.all_coins:
            default_items.append(int(round(c.current_price)))
            print(default_items)
        data = {
            "labels": labels,
            "default": default_items,
            "coins": CoinPrices.objects.all().count(),
            'ltc_chart': ltc_chart,
            'btc_chart': btc_chart,
            'eth_chart': eth_chart
        }
        return Response(data)
