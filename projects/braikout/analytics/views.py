""" View displaying users historical and current trading history """
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from dashboard.models import CoinPrices


def intraday(request):
    """ View for intra-day trades to be visualised """
    all_coins = CoinPrices.objects.all()
    context = {'all_coins': all_coins}
    return render(request, 'analytics/analytics.html', context)


def daily(request):
    """ View for daily trades to be visualised """
    all_coins = CoinPrices.objects.all()
    context = {'all_coins': all_coins}
    return render(request, 'analytics/dailyAnalytics.html', context)


class ChartData(APIView):
    """ Chart data for visualisation of trades """

    def get(self, request, format=None):
        """ getter for Ajax function to retrieve this data """

        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        dynamoTable = dynamodb.Table('trade_stats')
        dynamoTableDaily = dynamodb.Table('daily_trade_stats')
        try:
            response = dynamoTable.scan()
            daily_response = dynamoTableDaily.scan()
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Items']
            daily_item = daily_response['Items']
            daily_item = (sorted(daily_item,
                                 key=lambda x: datetime.strptime(
                                     x['date'], '%Y-%m-%d')))
            numtrades = 0
            btc = 0
            ltc = 0
            eth = 0
            eur = 0
            cny = 0
            gbp = 0
            sizes = []
            longs = 0
            shorts = 0
            mins = []
            arealabels = ['BTC', 'LTC', 'ETH', 'EUR', 'CNY', 'GBP']
            poslabels = ['Longs', 'Shorts']
            equity = []
            for i in item:
                global numtrades
                global sizes
                numtrades = numtrades + 1
                for val in i.values():
                    if val == 'BTC':
                        btc = btc + 1
                    if val == 'ETH':
                        eth = eth + 1
                    if val == 'LTC':
                        ltc = ltc + 1
                    if val == 'GBP':
                        gbp = gbp + 1
                    if val == 'EUR':
                        eur = eur + 1
                    if val == 'CNY':
                        cny = cny + 1

                for key, val in i.items():
                    if key == 'min':
                        mins.append(val)
                    if key == 'pos':
                        if val == 'Long':
                            longs = longs + 1
                        else:
                            shorts = shorts + 1
                    if key == 'size':
                        sizes.append(val)
                    if key == 'equity':
                        equity.append(val)
            areas = [btc, ltc, eth, eur, cny, gbp]

            avg_size = 0
            for s in sizes:
                avg_size += s
            avg_size_final = avg_size / len(sizes)

            counters = []
            counter = 1
            for e in equity:
                counters.append(counter)
                counter += 1

            trades_made_daily = []
            dates_daily = []
            sizes_daily = []
            longs_daily = []
            shorts_daily = []
            for i in daily_item:
                for key, val in i.items():
                    if key == 'date':
                        dates_daily.append(val)
                    if key == 'avg_size':
                        sizes_daily.append(int(val))
                    if key == 'longs':
                        longs_daily.append(int(val))
                    if key == 'shorts':
                        shorts_daily.append(int(val))
                    if key == 'trades_made':
                        trades_made_daily.append(int(val))

            pos = [longs, shorts]

            data = {
                "areas": areas,
                "labels": arealabels,
                "pos_labels": poslabels,
                "pos_data": pos,
                "equity": equity,
                "equity_labels": counters,
                "daily_dates": dates_daily,
                "sizes_daily": sizes_daily,
                "longs_daily": longs_daily,
                "shorts_daily": shorts_daily,
                "trades_daily": trades_made_daily,
                'BTC': btc, 'ETH': eth, 'LTC': ltc, 'EUR': eur,
                'GBP': gbp, 'CNY': cny, 'trades_made': numtrades,
                'longs': longs, 'shorts': shorts,
                'avg_size': avg_size_final
            }
            return Response(data)
