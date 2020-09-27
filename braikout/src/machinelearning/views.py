""" Machine learning visualiser """
import datetime
import json

import boto3
from botocore.exceptions import ClientError
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import CoinPrices
from dashboard.views import DecimalEncoder


def get_stats(coin_id_tag):
    """
    Fetch data to visualise from Dynamo DB database

    :param coin_id_tag: ID of coin to lookup
    :type coin_id_tag str

    :return: List of trade statistics
    :rtype List
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamotable = dynamodb.Table('forexstats')
    now = datetime.datetime.now()

    try:
        response = dynamotable.get_item(
            Key={
                'date': now.strftime("%Y-%m-%d"),
                'coin_id': coin_id_tag
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])

    else:
        item = response['Item']
        jsondata = json.loads(json.dumps(item, indent=4, cls=DecimalEncoder))

        avg_loss = str(jsondata['avg_loss_trade'])
        avg_win = str(jsondata['avg_win_trade'])
        largest_loss = str(jsondata['largest_loss_trade'])
        largest_win = str(jsondata['largest_win_trade'])
        loss_trades = str(jsondata['loss_trades'])
        net_prof = str(jsondata['net_prof'])
        percent_profit = str(jsondata['percent_profit'])
        profit_factor = str(jsondata['profit_factor'])
        win_trades = str(jsondata['win_trades'])

        return[avg_loss, avg_win, largest_loss, largest_win, loss_trades,
               win_trades, net_prof, percent_profit, profit_factor]

btc_prof = 0
eth_prof = 0
ltc_prof = 0
dlen = 0


def visualisation(request):
    """ Home page of all coins to visualise """
    all_coins = CoinPrices.objects.all()
    context = {'all_coins': all_coins}
    return render(request, 'machinelearning/visualisation.html', context)


def btc_predictions(request):
    """ bitcoin backtesting results """
    all_coins = CoinPrices.objects.all()
    prof = str(round(float(btc_prof), 2))
    context = {'all_coins': all_coins, 'prof': prof, 'dlen': dlen}
    return render(request, 'machinelearning/BTC_predictions.html', context)


def ltc_predictions(request):
    """ litecoin backtesting results """
    all_coins = CoinPrices.objects.all()
    prof = str(round(float(ltc_prof), 2))
    context = {'all_coins': all_coins, 'prof': prof, 'dlen': dlen}
    return render(request, 'machinelearning/LTC_predictions.html', context)


def eth_predictions(request):
    """ ethereum backtesting results """
    all_coins = CoinPrices.objects.all()
    prof = str(round(float(eth_prof), 2))
    context = {'all_coins': all_coins, 'prof': prof, 'dlen': dlen}
    return render(request, 'machinelearning/ETH_predictions.html', context)


def eur_predictions(request):
    """ euro backtesting results """
    all_coins = CoinPrices.objects.all()
    stats = get_stats('eur')
    context = {'all_coins': all_coins, 'stats': stats}
    return render(request, 'machinelearning/EUR_predictions.html', context)


def gbp_predictions(request):
    """ pound backtesting results """
    all_coins = CoinPrices.objects.all()
    stats = get_stats('gbp')
    context = {'all_coins': all_coins, 'stats':stats}
    return render(request, 'machinelearning/GBP_predictions.html', context)


class ChartData(APIView):
    """ chart data for machine learning predictions to be visualised """
    global btc_prof, eth_prof, ltc_prof, dlen

    def get(self, request, format=None):
        """ gets machine learning data and passes to Ajax function """
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        dynamotable = dynamodb.Table('mlpredstats')
        try:
            response = dynamotable.scan()
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            btc_dict = {}
            eth_dict = {}
            ltc_dict = {}
            dates_daily = []
            dates_daily_pred = []

            item = response['Items']
            item = (sorted(item, key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d')))
            for i in item:
                for key, val in i.items():
                    if key == 'date':
                        dates_daily.append(val)
                        dates_daily_pred.append(val)
                    if val == 'btc':
                        for key, val in i.items():
                            btc_dict.update({key: val})
                    if val == 'eth':
                        for key, val in i.items():
                            eth_dict.update({key: val})
                    if val == 'ltc':
                        for key, val in i.items():
                            ltc_dict.update({key: val})

            dates_daily_pred.append("NEW")
            btc_reals = (btc_dict['actual'].replace('[', ""))
            btc_reals = btc_reals.replace(']', "").split()
            eth_reals = (eth_dict['actual'].replace('[', ""))
            eth_reals = eth_reals.replace(']', "").split()
            ltc_reals = (ltc_dict['actual'].replace('[', ""))
            ltc_reals = ltc_reals.replace(']', "").split()


            global btc_prof, eth_prof, ltc_prof, dlen

            btc_preds = (btc_dict['preds'].replace('[', ""))
            btc_preds = btc_preds.replace(']', "").split()
            eth_preds = (eth_dict['preds'].replace('[', ""))
            eth_preds = eth_preds.replace(']', "").split()
            ltc_preds = (ltc_dict['preds'].replace('[', ""))
            ltc_preds = ltc_preds.replace(']', "").split()

            btc_wins = btc_dict['wins']
            btc_loss = btc_dict['loss']
            eth_wins = eth_dict['wins']
            eth_loss = eth_dict['loss']
            ltc_wins = ltc_dict['wins']
            ltc_loss = ltc_dict['loss']
            btc_prof = btc_dict['prof']
            eth_prof = eth_dict['prof']
            ltc_prof = ltc_dict['prof']

            dates = reversed([(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                              for i in range(len(btc_preds)-1)])

            btc_winloss = [btc_wins, btc_loss]
            eth_winloss = [eth_wins, eth_loss]
            ltc_winloss = [ltc_wins, ltc_loss]

            data = {
                "btcreals": btc_reals,
                "ethreals": eth_reals,
                "ltcreals": ltc_reals,
                "btcpreds": btc_preds,
                "ethpreds": eth_preds,
                "ltcpreds": ltc_preds,
                'btcwins': btc_wins,
                'btcloss': btc_loss,
                'btcwinloss': btc_winloss,
                'btcprof': btc_prof,
                'ethwins': eth_wins,
                'ethloss': eth_loss,
                'ethwinloss': eth_winloss,
                'ethprof': eth_prof,
                'ltcwins': ltc_wins,
                'ltcloss': ltc_loss,
                'ltcwinloss': ltc_winloss,
                'ltcprof': ltc_prof,
                "daily_dates": dates_daily,
                "daily_dates_pred": dates,
            }
            return Response(data)


