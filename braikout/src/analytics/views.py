""" View displaying users historical and current trading history """
from collections import defaultdict
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from dashboard.models import CoinPrices


def intraday(request):
    """
    View for intra-day trades to be visualised

    :param request: Django request
    :type request: request

    :return: render analytics view
    """
    all_coins = CoinPrices.objects.all()
    context = {'all_coins': all_coins}
    return render(request, 'analytics/analytics.html', context)


def daily(request):
    """
    View for daily trades to be visualised

    :param request: Django request
    :type request: request

    :return: render daily analytics view
    """
    all_coins = CoinPrices.objects.all()
    context = {'all_coins': all_coins}
    return render(request, 'analytics/dailyAnalytics.html', context)


class ChartData(APIView):

    def get(self, request, format=None):
        """
        getter for Ajax function to retrieve this data

        :param request: Django request
        :type request: request

        :param format: Format of request (if specifc, default=Json)
        :type format: str

        :return: Response Data for Chart rendering
        :rtype: Response
        """

        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        dynamoTable = dynamodb.Table('trade_stats')
        dynamoTableDaily = dynamodb.Table('daily_trade_stats')
        try:
            response = dynamoTable.scan()
            daily_response = dynamoTableDaily.scan()
        except ClientError as e:
            raise Exception(e)
        else:
            item = response['Items']
            daily_item = daily_response['Items']
            daily_item = (sorted(daily_item,
                                 key=lambda x: datetime.strptime(
                                     x['date'], '%Y-%m-%d')))
            numtrades = 0
            longs = 0
            shorts = 0
            mins = []
            equity = []
            sizes = []

            coin_dict = defaultdict(int)

            for i in item:
                numtrades += 1
                for val in i.values():
                    coin_dict[val] += 1

                for key, val in i.items():
                    if key == 'min':
                        mins.append(val)
                    if key == 'pos':
                        if val == 'Long':
                            longs += 1
                        else:
                            shorts += 1
                    if key == 'size':
                        sizes.append(val)
                    if key == 'equity':
                        equity.append(val)

            counters = [i + 1 for i in range(len(equity))]
            data = self._build_data(equity, counters, coin_dict, longs, shorts,
                                    numtrades, sum(sizes) / len(sizes), daily_item)
            return Response(data)

    def _process_analytics(self, daily_item):
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

        return trades_made_daily, dates_daily, sizes_daily, longs_daily, shorts_daily

    def _build_data(self, equity, counters, coin_dict, longs, shorts, numtrades,
                    avg_size_final, daily_item):

        trades_made_daily, dates_daily, sizes_daily, longs_daily, shorts_daily = self._process_analytics(daily_item)
        return {
            "areas": coin_dict,
            "labels": coin_dict.keys(),
            "pos_labels": ['Longs', 'Shorts'],
            "pos_data": [longs, shorts],
            "equity": equity,
            "equity_labels": counters,
            "daily_dates": dates_daily,
            "sizes_daily": sizes_daily,
            "longs_daily": longs_daily,
            "shorts_daily": shorts_daily,
            "trades_daily": trades_made_daily,
            'BTC': coin_dict['BTC'], 'ETH': coin_dict['ETH'],
            'LTC': coin_dict['LTC'], 'EUR': coin_dict['EUR'],
            'GBP': coin_dict['GBP'], 'CNY': coin_dict['CNY'],
            'trades_made': numtrades,
            'longs': longs, 'shorts': shorts,
            'avg_size': avg_size_final
        }
