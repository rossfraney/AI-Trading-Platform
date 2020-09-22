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
    dynamo_db = boto3.resource('dynamodb', region_name='us-east-2')
    dynamo_tables = dynamo_db.Table('auth')
    if auth_key.is_valid():
        text, text1, text2, text3 = [auth_key.cleaned_data[f'post{i}'] for i in range(4)]

        dynamo_tables.put_item(
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


def is_crypto(coin_id):
    return coin_id < 5


def handle_auth(request, dynamo_db):
    username = request.user.username
    dynamo_table_auth = dynamo_db('auth')
    try:
        return dynamo_table_auth.get_item(
            Key={
                'username': username
            }
        )
    except ClientError:
        return shortcuts.redirect('/dashboard/auth-keys')


def get_response_data(coin, coin_id, table):
    single_prediction_table = table('crypto_prediction')
    all_predictions_table = table('crypto_predictions')
    coin_id_tag = coin.ticker.lower()
    now = datetime.datetime.now()

    try:
        response = single_prediction_table.get_item(
            Key={
                'date': now.strftime("%Y-%m-%d"),
                'coin_id': coin_id_tag
            }
        )
        response_charts = None
        if coin_id < 4:
            response_charts = all_predictions_table.get_item(
                Key={
                    'coin_id': coin_id_tag
                }
            )
    except ClientError as e:
        return shortcuts.redirect('/dashboard/auth-keys')

    return response, response_charts


def get_trading_data(coin_id_tag):
    dynamo_db = boto3.resource('dynamodb', region_name='us-east-2')
    dynamo_tables = dynamo_db.Table('crypto_predictions')
    try:
        response = dynamo_tables.get_item(
            Key={
                'coin_id': coin_id_tag
            }
        )
        return response['Item']
    except ClientError as e:
        print(e.response['Error']['Message'])


def update_current_trend(coin, coin_id, json_data, json_data_charts):
    """
    Updates db with current trend state
    """
    if coin_id < 4:
        pred_price = float("{0:.2f}".format(json_data['pred']))
        coin_resi = str(json_data_charts['resi'])
        coin_support = str(json_data_charts['support'])

        CoinPrices.objects.filter(pk=coin_id).update(predictions=pred_price)
        price = CryptoApi.get_prices(coin.ticker, 'usd')['last']

        CoinPrices.objects.filter(pk=coin_id).update(trend="Tightening")
        if price > coin_resi:
            CoinPrices.objects.filter(pk=coin_id).update(trend="Bullish")
        if price < coin_support:
            CoinPrices.objects.filter(pk=coin_id).update(trend="Bearish")


def index(request):
    """This is the view which represents the dashboard page.
    It indexes every other app on the platform"""

    table = boto3.resource('dynamodb', region_name='us-east-2').Table
    handle_auth(request, table)

    for coin_id in range(1, 6):
        coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)

        if is_crypto(coin_id):
            curr_price = CryptoApi.get_prices(str(coin.ticker), "usd")['last']
            CoinPrices.objects.filter(pk=coin_id).update(current_price=curr_price)
        else:
            last_price = CurrencyRates().get_rates('USD')['GBP']
            CoinPrices.objects.filter(pk=5).update(current_price=last_price)

        response, response_charts = get_response_data(coin, coin_id, table)

        json_data = json.loads((json.dumps(response['Item'], indent=4, cls=DecimalEncoder)))
        json_data_charts = json.loads((json.dumps(response_charts['Item'], indent=4, cls=DecimalEncoder)))

        update_current_trend(coin, coin_id, json_data, json_data_charts)

    all_coins = CoinPrices.objects.all()

    for c in all_coins:
        sentiment = sum(Scraper.analyze_tweets_numerical(c.ticker)[0:3])
        CoinPrices.objects.filter(ticker=c.ticker).update(sentiment_score=round(sentiment, 2))

    tables.RequestConfig(request).configure(CoinTable(all_coins))
    return shortcuts.render(request, 'dashboard/index.html',
                            {'all_coins': all_coins,
                             'table': table,
                             'equity': round(CryptoApi.get_equity(), 2)})


def get_support_res_from_json(json_data_charts):
    coin_resistance = str(json_data_charts['resi'])
    coin_support = str(json_data_charts['support'])
    coin_resistance_2 = str(json_data_charts['resi2'])
    coin_support2 = str(json_data_charts['support2'])
    return [coin_resistance, coin_support, coin_resistance_2, coin_support2]


def make_buy(buy, coin, dynamo_table):
    if buy.is_valid():
        text = buy.cleaned_data['post']
        buy = BuyForm()
        CryptoApi.buy_crypto(text, coin.ticker)
        update_balance_table(dynamo_table)


def make_sell(sell, coin, dynamo_table):
    if sell.is_valid():
        text = sell.cleaned_data['post']
        sell = SellForm()
        CryptoApi.sell_crypto(text, coin.ticker)
        update_balance_table(dynamo_table)


def update_balance_table(dynamo_table):
    time.sleep(5)
    wallet = CryptoApi.get_balance_eq()
    for key, val in wallet.items():
        dynamo_table.put_item(
            Item={
                'coin_id': key,
                'amount': val
            }
        )


def detail(request, coin_id):

    """ This is the view corresponding to the cryptocurrency trading page,
     and details of the analysis the platform provides. I.e, Price predictions,
     chart analysis results, and sentiment analysis """

    coin = shortcuts.get_object_or_404(CoinPrices, pk=coin_id)
    all_coins = CoinPrices.objects.all()
    coin_id_tag = coin.ticker.lower()

    if int(coin_id) >= 4:
        return shortcuts.redirect('/dashboard/auth-keys')

    item = get_trading_data(coin_id_tag)
    json_data_charts = json.loads(json.dumps(item, indent=4, cls=DecimalEncoder))
    trend_data = get_support_res_from_json(json_data_charts)

    price = CryptoApi.get_prices(coin.ticker, 'usd')['last']
    if price > trend_data[0]:
        CoinPrices.objects.filter(pk=coin_id).update(trend="Bullish")
    if price < trend_data[1]:
        CoinPrices.objects.filter(pk=coin_id).update(trend="Bearish")
    all_coins = CoinPrices.objects.all()

    wallet = CryptoApi.get_balance_eq()

    buy = BuyForm(request.POST, prefix='buy')
    sell = SellForm(request.POST, prefix='sell')

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamo_table = dynamodb.Table('wallet')

    make_buy(buy, coin, dynamo_table)
    make_sell(sell, coin, dynamo_table)

    pos_neg_next_day = coin.current_price - coin.predictions

    return shortcuts.render(request, 'dashboard/detail.html', {
        'coin': coin, 'all_coins': all_coins,
        'wallet': wallet, 'b_form': BuyForm(prefix='buy'),
        's_form': SellForm(prefix='sell'),
        'pos_neg_next_day': pos_neg_next_day, 'resi': trend_data[0],
        'support': trend_data[1], 'resi2': trend_data[2],
        'support2': trend_data[3]
    })


# TODO Next is Forex Refactor
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

    dict = {s for s in ForexApi.get_pos()['positions']}
    instrument = None
    units = None
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
        row_attrs = {'data-id': lambda coinprices: coinprices.ticker.lower()}
        exclude = ('coin_logo', 'id', 'is_favorite',)
        template_name = 'django_tables2/bootstrap.html'
