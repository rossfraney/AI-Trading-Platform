""" Views for trading and dashboard page """
import datetime
import decimal
import json
import time

import boto3 as boto3
import django_tables2 as tables

import django.shortcuts as shortcuts
from botocore.exceptions import ClientError
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from forex_python.converter import CurrencyRates

from dashboard import CryptoApi, ForexApi
from sentiment import Scraper
from braikout.forms import BuyForm, AlertAboveForm, AlertBelowForm, AuthForm
from braikout.forms import SellForm

from .models import CoinPrices

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
dynamoTable = dynamodb.Table('wallet')


class DecimalEncoder(json.JSONEncoder):
    """ Decimal encoder default class """
    def default(self, o):
        """Helper class to convert a DynamoDB item to JSON."""
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            return int(o)
        return super(DecimalEncoder, self).default(o)


def auth(request):
    """ Takes user input for auth """
    auth_key = AuthForm(request.POST, prefix='cryp_auth')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('auth')
    if auth_key.is_valid():
        text = auth_key.cleaned_data['post']
        text1 = auth_key.cleaned_data['post1']
        text2 = auth_key.cleaned_data['post2']
        text3 = auth_key.cleaned_data['post3']
        dynamoTables.put_item(
            Item={"username": request.user.username,
                    "cryptoapi": text,
                    "cryptosec": text1,
                    "fxapi": text2,
                    "fxsec": text3,
                  }
        )
        return shortcuts.redirect("/")

    return shortcuts.render(request, 'dashboard/auth.html', {
        'auth_form': AuthForm(prefix='cryp_auth'),
        'auth_form_sec': AuthForm(prefix='cryp_sec'),
        'auth_form_fx': AuthForm(prefix='fx_auth'),
        'auth_form_fx_sec': AuthForm(prefix='fx_sec'),
        'username_form': AuthForm(prefix='username')
    })


def index(request):
    """This is the view which represents the dashboard page.
    It indexes every other app on the platform"""
    # def say(message):
    #     pythoncom.CoInitialize()
    #     engine = pyttsx3.init()
    #     engine.say(message)
    #     engine.runAndWait()
    username = request.user.username
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('crypto_prediction')
    dynamoTables = dynamodb.Table('crypto_predictions')
    dynamoTableAuth = dynamodb.Table('auth')
    try:
        response_auth = dynamoTableAuth.get_item(
            Key={
                'username': username
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return shortcuts.redirect('/dashboard/auth-keys')
    else:
        pass

    for i in range(1, 6):
        coin_id = i
        coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)
        try:
            from json.decoder import JSONDecodeError as Js_error
        except ImportError:
            Js_error = ValueError
        if i < 5:
            prices = CryptoApi.get_prices(str(coin.ticker), "usd")
            last_price = prices['last']
            CoinPrices.objects.filter(pk=coin_id).update(current_price=last_price)
        if 4 < i < 6:
            c = CurrencyRates()
            c_dict = c.get_rates('USD')
            last_price = c_dict['GBP']
            CoinPrices.objects.filter(pk=5).update(current_price=last_price)

        coin_id_tag = coin.ticker.lower()
        now = datetime.datetime.now()
        try:
            response = dynamoTable.get_item(
                Key={
                    'date': now.strftime("%Y-%m-%d"),
                    'coin_id': coin_id_tag
                }
            )
            if coin_id < 4:
                response_charts = dynamoTables.get_item(
                    Key={
                        'coin_id': coin_id_tag
                    }
                )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Item']
            item2 = response_charts['Item']

            chart = (json.dumps(item, indent=4, cls=DecimalEncoder))
            chart2 = (json.dumps(item2, indent=4, cls=DecimalEncoder))
            json_data = json.loads(chart)
            json_data_charts = json.loads(chart2)
            pred_price = float("{0:.2f}".format(json_data['pred']))
            coin_resi = str(json_data_charts['resi'])
            coin_support = str(json_data_charts['support'])

            if i < 4:
                CoinPrices.objects.filter(pk=coin_id).update(predictions=pred_price)
                price = CryptoApi.get_prices(coin.ticker, 'usd')['last']
                CoinPrices.objects.filter(pk=coin_id).update(trend="Tightening")
                if price > coin_resi:
                    CoinPrices.objects.filter(pk=coin_id).update(trend="Bullish")
                if price < coin_support:
                    CoinPrices.objects.filter(pk=coin_id).update(trend="Bearish")
                all_coins = CoinPrices.objects.all()

    all_coins = CoinPrices.objects.all()
    for c in all_coins:
        result = Scraper.analyze_tweets_numerical(c.ticker)
        senti_score =result[0] + result[1] + result[2]
        CoinPrices.objects.filter(ticker=c.ticker).update(sentiment_score=round(senti_score, 2))
    table = CoinTable(all_coins)
    tables.RequestConfig(request).configure(table)

    equity = CryptoApi.get_equity()

    context = {'all_coins': all_coins, 'table': table, 'equity': round(equity, 2)}
    # say("Welcome to Braikout Dashboard")
    # say("Current total Equity is. " + str(equity) + " dollars")
    return shortcuts.render(request, 'dashboard/index.html', context)


def detail(request, coin_id):

    """ This is the view corresponding to the cryptocurrency trading page,
     and details of the analysis the platform provides. I.e, Price predictions,
     chart analysis results,
    and sentiment analysis """


    global coin_support2, coin_resistance_2, all_coins, coin_resistance
    coin_resistance = ""
    coin_support = ""
    coin_resistance_2 = ""
    coin_support2 = ""

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('crypto_predictions')
    coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)
    all_coins = CoinPrices.objects.all()
    coin_id_tag = coin.ticker.lower()
    if int(coin_id) < 4:
        try:
            response = dynamoTables.get_item(
                Key={
                    'coin_id': coin_id_tag
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Item']
            result = (json.dumps(item, indent=4, cls=DecimalEncoder))
            json_data_charts = json.loads(result)
            coin_resistance = str(json_data_charts['resi'])
            coin_support = str(json_data_charts['support'])
            coin_resistance_2 = str(json_data_charts['resi2'])
            coin_support2 = str(json_data_charts['support2'])
            price = CryptoApi.get_prices(coin.ticker, 'usd')['last']
            if price > coin_resistance:
                CoinPrices.objects.filter(pk=coin_id).update(trend="Bullish")
            if price < coin_support:
                CoinPrices.objects.filter(pk=coin_id).update(trend="Bearish")
            all_coins = CoinPrices.objects.all()

    wallet = CryptoApi.get_balance_eq()

    buy = BuyForm(request.POST, prefix='buy')
    sell = SellForm(request.POST, prefix='sell')
    if buy.is_valid():
        text = buy.cleaned_data['post']
        buy = BuyForm()
        CryptoApi.buy_crypto(text, coin.ticker)
        time.sleep(5)
        wallet = CryptoApi.get_balance_eq()
        for key, val in wallet.items():
            dynamoTable.put_item(
                Item={
                    'coin_id': key,
                    'amount': val
                }
            )
    if sell.is_valid():
        text = sell.cleaned_data['post']
        sell = SellForm()
        CryptoApi.sell_crypto(text, coin.ticker)
        time.sleep(5)
        wallet = CryptoApi.get_balance_eq()
        for key, val in wallet.items():
            dynamoTable.put_item(
                Item={
                    'coin_id': key,
                    'amount': val
                }
            )
    pos_neg_next_day = coin.current_price - coin.predictions

    return shortcuts.render(request, 'dashboard/detail.html', {
        'coin': coin, 'all_coins': all_coins,
        'wallet': wallet, 'b_form': BuyForm(prefix='buy'),
        's_form': SellForm(prefix='sell'),
        'pos_neg_next_day': pos_neg_next_day, 'resi': coin_resistance,
        'support': coin_support, 'resi2': coin_resistance_2,
        'support2': coin_support2
    })


def forex(request, coin_id):
    """ This is the view corresponding to the FX trading page,
    and details of the analysis the platform provides. I.e, Price predictions,
    chart analysis results, and sentiment analysis """
    coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)
    all_coins = CoinPrices.objects.all()

    wallet = CryptoApi.get_balance_eq()
    text = 0.0
    buy = BuyForm(request.POST, prefix='buy')
    sell = SellForm(request.POST, prefix='sell')
    if buy.is_valid():
        text = buy.cleaned_data['post']
        buy = BuyForm()
        ForexApi.buy_order(str(coin.ticker + "_USD"), text, coin.ticker)
        wallet = CryptoApi.get_balance_eq()
        time.sleep(5)

    if sell.is_valid():
        text = sell.cleaned_data['post']
        sell = SellForm()
        ForexApi.sell_order(str(coin.ticker + "_USD"))
        wallet = CryptoApi.get_balance_eq()
        time.sleep(5)

    positions = ForexApi.get_pos()['positions']
    dict = {}
    for s in positions:
        dict = s

    instrument = " "
    units = " "
    if 'instrument' in dict:
        instrument = dict['instrument']
        units = dict['long']['units']

    return shortcuts.render(request, 'dashboard/forex.html', {
        'coin': coin, 'all_coins': all_coins,
        'wallet': wallet, 'b_form': BuyForm(prefix='buy'),
        's_form': SellForm(prefix='sell'), 'trade_amount': text,
        'instrument': instrument, 'units': units
    })


def store_alert_above(text, ticker):
    """ Stores user alerts above current price in Dynamo DB table"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('alerts')
    dynamoTable.put_item(
        Item={
            'coin_id': ticker,
            'alert_above': decimal.Decimal(str(text))
        }
    )


def store_alert_below(text, ticker):
    """ Stores user alerts below current price in Dynamo DB table"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('alerts')
    dynamoTable.put_item(
        Item={
            'coin_id': ticker,
            'alert_below': decimal.Decimal(str(text))
        }
    )


def alerts(request, coin_id):
    """ Takes user input for alerts """
    coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)
    all_coins = CoinPrices.objects.all()

    alert_above = AlertAboveForm(request.POST, prefix='above')
    alert_below = AlertBelowForm(request.POST, prefix='below')

    if alert_above.is_valid():
        text = alert_above.cleaned_data['post']
        alert_above = AlertAboveForm
        store_alert_above(text, coin.ticker)

    if alert_below.is_valid():
        text = alert_below.cleaned_data['post']
        alert_below = AlertBelowForm
        store_alert_below(text, coin.ticker)

    return shortcuts.render(request, 'dashboard/alerts.html', {
        'coin': coin, 'all_coins': all_coins,
        'a_form': AlertAboveForm(prefix='above'),
        'b_form': AlertBelowForm(prefix='below')})


class ChartData(UpdateAPIView):
    """ Chart data for JSCharts """
    def get(self, request, format=None):
        """ Returns data from view to Ajax function
        for visual representation """
        all_coins = CoinPrices.objects.all()
        wallet = CryptoApi.get_balance_eq()
        labels = list(wallet.keys())
        value = list(wallet.values())
        senti_labels = []
        pred_labels = []
        senti_values = []
        predicted_change = []

        for coin in all_coins:
            senti_labels.append(str(coin.ticker))
            if coin.is_favorite and coin.ticker != 'EUR':
                pred_labels.append(str(coin.ticker))
            senti_values.append(float(coin.sentiment_score))
            a = coin.predictions
            c = coin.current_price
            if a == c:
                if coin.is_favorite and coin.ticker != 'EUR':
                    predicted_change.append(0)
            price_check = (abs(float((a - c) / c))) * 100
            if a > c:
                current_biggest_diff = price_check
            else:
                current_biggest_diff = -1 * price_check
            if coin.is_favorite and coin.ticker != 'EUR':
                predicted_change.append(current_biggest_diff)

        length = len(labels)
        i = 0
        while i < length:
            if labels[i] == 'usd':
                i = i + 1
            else:
                prices = CryptoApi.get_prices(labels[i], "usd")
                last_price = prices['last']
                value[i] = float(value[i]) * float(last_price)
                i = i + 1
        data = {
            "labels": labels,
            "senti_labels": senti_labels,
            "pred_labels": pred_labels,
            "default": value,
            "senti_default": senti_values,
            "predicted_change": predicted_change,
        }
        return Response(data)


class CoinTable(tables.Table):
    """ Table for dashboard """
    class Meta:
        model = CoinPrices
        row_attrs = {
            'data-id': lambda coinprices: coinprices.ticker.lower()
        }
        exclude = ('coin_logo', 'id', 'is_favorite',)
        template_name = 'django_tables2/bootstrap.html'
