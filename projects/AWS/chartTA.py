import base64
import bitstamp.client
import pandas as pd
import time
import seaborn as sns
import datetime
import numpy as np
import sys
from PIL import Image
import io
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os
import boto3
from decimal import Decimal



from matplotlib import dates
from matplotlib.finance import candlestick_ohlc



ltc_chart = []
btc_chart = []
eth_chart = []

def mlrun():
    yesterday = date.today() - timedelta(1)
    #################################################################################
    # TODO - Download images locally
    yesterday = datetime.datetime.now() - timedelta(days=60)
    bull = False
    bear = False
    tightening = False
    inconclusive = True
    states = " "

    def get_change(a, b):
       # print(abs(100 * (b - a) / a))
       return abs(100 * (b - a) / a)


    def check_init_low(coinid, x, set, states, currentHigh, currentLow):
        print(str("check_init_low " + str(currentLow) + " = low, " + str(currentHigh) + "= high"))
        close = []
        lows = []
        highs = []
        srlines = []

        while x > 0:
            close.append(set['Close'][x])
            lows.append(set['Low'][x])
            highs.append(set['High'][x])
            x -= 1

        print(close)
        print(highs)
        print(lows)
        dupes = close

        for s in close:
            for i in dupes:
                if get_change(s, i) < 5.0:
                    srlines.append(i)

        dupes = highs
        for s in highs:
            for i in dupes:
                if get_change(s, i) < 5.0:
                    srlines.append(i)

        dupes = lows
        for s in lows:
            for i in dupes:
                if get_change(s, i) < 5.0:
                    srlines.append(i)

        resi = set['High'][59]
        support = set['Low'][59]
        resis = []
        supports = []
        public_client = bitstamp.client.Public()

        prices = set['Close'][0]
        print(float(prices))
        for s in srlines:
            if s < float(prices):
                # print(" Support = " + str(s))
                supports.append(s)
            if s > float(prices):
                # print(" Resistance = " + str(s))
                resis.append(s)

        resis = sorted(resis)
        supports = sorted(supports)

        resi = resis[0]
        support = supports[0]

        for r in resis:
            if r < resi:
                resi = r
        for s in supports:
            if s > support:
                support = s

        resi2 = resis[1]
        support2 = supports[1]

        print("Resi 1 = " + str(resi))
        print("Resi 2 = " + str(resi2))
        print("Support 1 = " + str(support))
        print("Support 2 = " + str(support2))

        if support < float(prices) < resi:
            states = "tightening" 

        if support > float(prices):
            states = "bear" 

        if resi < float(prices):
            states = "bull"

        now = datetime.datetime.now()
        dynamodb = boto3.resource('dynamodb')
        dynamoTable = dynamodb.Table('crypto_predictions')

        dynamoTable.put_item(
        Item = {
            'coin_id' : str(coinid), 
            'trend': str(states), 
            'resi' : Decimal(str(resi)), 
            'support': Decimal(str(support)),
            'resi2' : Decimal(str(resi2)), 
            'support2': Decimal(str(support2))
        })

        return states

    def check_candle(x, set):
        print("in check candle")
        if set['Open'][x] > set['Close'][x]:
            if not is_doji(x, set):
                print("red")
                return 'red'
            else:
                print("doji")
                return 'doji'
        else:
            if not is_doji(x, set):
                print("green")
                return 'green'


    def check_candle(x, set):
        print("in check candle")
        if set['Open'][x] > set['Close'][x]:
            if not is_doji(x, set):
                print("red")
                return 'red'
            else:
                print("doji")
                return 'doji'
        else:
            if not is_doji(x, set):
                print("green")
                return 'green'


    def is_doji(x, set):
        print(" in is doji ")
        middle = abs(set['Open'][x] - set['Close'][x])
        print(" Middle bit = " + str(middle))
        if set['Open'][x] < set['Close'][x]:
            top_spike = set['High'][x] - set['Close'][x]
            bottom_spike = set['Low'][x] - set['Open'][x]
            print(" First case")
            print(" top bit = " + str(top_spike))
            print(" bottom bit = " + str(bottom_spike))
        else:
            top_spike = set['High'][x] - set['Open'][x]
            bottom_spike = set['Close'][x] - set['Low'][x]
            print(" Second case")
            print(" top bit = " + str(top_spike))
            print(" bottom bit = " + str(bottom_spike))

        if top_spike + bottom_spike > middle:
            return True
        else:
            return False


    bitcoin_market_info = pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start="+yesterday.strftime('%Y%m%d')
                                   +"&end="+ time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')
    print(bitcoin_market_info.head())

    bitcoin_market_info['100ma'] = bitcoin_market_info['Close'].rolling(window = 100, min_periods=0).mean()
    # resampling
    btc_ohlc = bitcoin_market_info['Close'].resample('7D').ohlc()
    btc_df_volume = bitcoin_market_info['Volume'].resample('1D').sum()
    btc_ohlc.reset_index(inplace=True)
    bitcoin_market_info.reset_index(inplace=True)
    btc_ohlc['Date'] = btc_ohlc['Date'].map(dates.date2num)
    bitcoin_market_info['Date'] = bitcoin_market_info['Date'].map(dates.date2num)
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=5, facecolor='#00004d')
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    ax1.xaxis_date()
    candlestick_ohlc(ax1, bitcoin_market_info.values, width=0.8, colorup='g')
    ax2.fill_between(btc_df_volume.index.map(dates.date2num), btc_df_volume.values, 0)
    btc_lows = bitcoin_market_info['Low']
    btc_highs = bitcoin_market_info['High']
    current_btc_Low = btc_lows[29]
    currentLow = current_btc_Low
    current_btc_High = btc_highs[29]
    currentHigh = current_btc_High
    print(check_init_low('btc', 59, bitcoin_market_info, " ", currentHigh, currentLow))
    print(states)
    global btc_chart
    btc_chart = btc_ohlc.to_json(orient='records', lines=True)
    figBtc = plt.gcf()
    canvasBtc = figBtc.canvas
    bufBtc, sizeBtc = canvasBtc.print_to_buffer()
    imageBtc = Image.frombuffer('RGBA', sizeBtc, bufBtc, 'raw', 'RGBA', 0, 1)
    buffer = io.BytesIO()
    imageBtc.save(buffer,'PNG')
    graphicBtc = buffer.getvalue()
    graphicBtc = base64.b64encode(graphicBtc)
    buffer.close()
    imgdata = base64.b64decode(graphicBtc)
    filename = 'images/BtcChart.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    f.close()




    eth_market_info = pd.read_html("https://coinmarketcap.com/currencies/ethereum/historical-data/?start="+yesterday.strftime('%Y%m%d')
                                   +"&end="+ time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    eth_market_info['Volume'] = eth_market_info['Volume'].astype('int64')
    print(eth_market_info.head())

    eth_market_info['100ma'] = eth_market_info['Close'].rolling(window = 100, min_periods=0).mean()
    # resampling
    eth_ohlc = eth_market_info['Close'].resample('7D').ohlc()
    eth_df_volume = eth_market_info['Volume'].resample('1D').sum()
    eth_ohlc.reset_index(inplace=True)
    eth_market_info.reset_index(inplace=True)
    eth_ohlc['Date'] = eth_ohlc['Date'].map(dates.date2num)
    eth_market_info['Date'] = eth_market_info['Date'].map(dates.date2num)
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=5, facecolor='#00004d')
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    ax1.xaxis_date()
    candlestick_ohlc(ax1, eth_market_info.values, width=0.8, colorup='g')
    ax2.fill_between(eth_df_volume.index.map(dates.date2num), eth_df_volume.values, 0)
    eth_lows = eth_market_info['Low']
    eth_highs = eth_market_info['High']
    current_eth_Low = eth_lows[29]
    currentLow = current_eth_Low
    current_eth_High = eth_highs[29]
    currentHigh = current_eth_High
    print(check_init_low('eth', 59, eth_market_info, " ", currentHigh, currentLow))
    print(states)
    global eth_chart
    eth_chart = eth_ohlc.to_json(orient='records', lines=True)
    figEth = plt.gcf()
    canvasEth = figEth.canvas
    bufEth, sizeEth = canvasEth.print_to_buffer()
    imageEth = Image.frombuffer('RGBA', sizeEth, bufEth, 'raw', 'RGBA', 0, 1)
    buffer = io.BytesIO()
    imageEth.save(buffer,'PNG')
    graphicEth = buffer.getvalue()
    graphicEth = base64.b64encode(graphicEth)
    buffer.close()
    imgdata = base64.b64decode(graphicEth)
    filename = 'images/EthChart.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    f.close()


    ltc_market_info = pd.read_html("https://coinmarketcap.com/currencies/litecoin/historical-data/?start="+yesterday.strftime('%Y%m%d')
                                   +"&end="+ time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    ltc_market_info['Volume'] = ltc_market_info['Volume'].astype('int64')
    print(ltc_market_info.head())

    ltc_market_info['100ma'] = ltc_market_info['Close'].rolling(window = 100, min_periods=0).mean()
    # resampling
    ltc_ohlc = ltc_market_info['Close'].resample('1D').ohlc()
    ltc_df_volume = ltc_market_info['Volume'].resample('1D').sum()
    ltc_ohlc.reset_index(inplace=True)
    ltc_market_info.reset_index(inplace=True)
    ltc_ohlc['Date'] = ltc_ohlc['Date'].map(dates.date2num)
    ltc_market_info['Date'] = ltc_market_info['Date'].map(dates.date2num)
    print(pd.json.dumps(ltc_market_info.head()))
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=5, facecolor='#00004d')
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    ax1.xaxis_date()
    candlestick_ohlc(ax1, ltc_market_info.values, width=0.8, colorup='g')
    ax2.fill_between(ltc_df_volume.index.map(dates.date2num), ltc_df_volume.values, 0)
    ltc_lows = ltc_market_info['Low']
    ltc_highs = ltc_market_info['High']
    current_ltc_Low = ltc_lows[29]
    currentLow = current_ltc_Low
    current_ltc_High = ltc_highs[29]
    currentHigh = current_ltc_High
    print(check_init_low('ltc', 59, ltc_market_info, " ", currentHigh, currentLow))
    print(states)
    global ltc_chart
    ltc_chart = ltc_ohlc.to_json(orient='records', lines=True)
    figLtc = plt.gcf()
    #plt.show()

    canvasLtc = figLtc.canvas
    bufLtc, sizeLtc = canvasLtc.print_to_buffer()
    imageLtc = Image.frombuffer('RGBA', sizeLtc, bufLtc, 'raw', 'RGBA', 0, 1)


    buffer = io.BytesIO()
    imageLtc.save(buffer,'PNG')
    graphicLtc = buffer.getvalue()
    graphicLtc = base64.b64encode(graphicLtc)
    buffer.close()

    imgdata = base64.b64decode(graphicLtc)
    filename = 'images/LtcChart.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    f.close()

    os.system('aws s3 sync /home/ubuntu/images s3://braikoutpredictions/Images --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers')


if __name__ == "__main__":
    mlrun()
