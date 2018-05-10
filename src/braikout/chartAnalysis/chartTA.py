import base64
from threading import Thread
# django.setup()

import pandas as pd
import time
import seaborn as sns
import datetime
import numpy as np
from legacy import xrange
from numpy import array
import sys
from PIL import Image
import io
import matplotlib.pyplot as plt
from datetime import date, timedelta
import json

from matplotlib import dates
from matplotlib.finance import candlestick_ohlc


from threading import Thread

ltc_chart = []
btc_chart = []
eth_chart = []


def mlrun():
    #################################################################################
    # TODO - Download images locally
    yesterday = datetime.datetime.now() - timedelta(days=60)
    bull = False
    bear = False
    tightening = False
    inconclusive = True
    states = " "

    def gentrends(x, window=1 / 3.0, charts=False):
        import numpy as np

        x = np.array(x)

        if window < 1:
            window = int(window * len(x))

        max1 = np.where(x == max(x))[0][0]  # find the index of the abs max
        min1 = np.where(x == min(x))[0][0]  # find the index of the abs min

        # First the max
        if max1 + window > len(x):
            max2 = max(x[0:(max1 - window)])
        else:
            max2 = max(x[(max1 + window):])

        # Now the min
        if min1 - window < 0:
            min2 = min(x[(min1 + window):])
        else:
            min2 = min(x[0:(min1 - window)])

        max2 = np.where(x == max2)[0][0]
        min2 = np.where(x == min2)[0][0]

        maxslope = (x[max1] - x[max2]) / (max1 - max2)
        minslope = (x[min1] - x[min2]) / (min1 - min2)
        a_max = x[max1] - (maxslope * max1)
        a_min = x[min1] - (minslope * min1)
        b_max = x[max1] + (maxslope * (len(x) - max1))
        b_min = x[min1] + (minslope * (len(x) - min1))
        maxline = np.linspace(a_max, b_max, len(x))
        minline = np.linspace(a_min, b_min, len(x))

        trends = np.transpose(np.array((x, maxline, minline)))
        # trends = pd.dataframe(trends, index=np.arange(0, len(x)),
        #                       columns=['Data', 'Max Line', 'Min Line'])

        if charts is True:
            from matplotlib.pyplot import plot, grid, show
            plot(trends)
            grid()
            show()

        print(trends, maxslope, minslope)
        return trends, maxslope, minslope


    bitcoin_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=" + yesterday.strftime('%Y%m%d')
                 + "&end=" + time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]

    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')

    bitcoin_market_info['100ma'] = bitcoin_market_info['Close'].rolling(window=100, min_periods=0).mean()

    bitcoin_market_info.reset_index(inplace=True)
    btc_ohlc = bitcoin_market_info.drop(bitcoin_market_info.columns[[5, 6, 7]],
                                        axis=1)  # df.columns is zero-based pd.Index
    print(btc_ohlc.head())

    btc_ohlc = btc_ohlc.rename(columns={'Date': 'date'})
    btc_ohlc = btc_ohlc.rename(columns={'Open': 'open'})
    btc_ohlc = btc_ohlc.rename(columns={'High': 'high'})
    btc_ohlc = btc_ohlc.rename(columns={'Low': 'low'})
    btc_ohlc = btc_ohlc.rename(columns={'Close': 'close'})

    ##Chart analysis
    btc_lows = bitcoin_market_info['Low']
    btc_highs = bitcoin_market_info['High']
    current_btc_Low = btc_lows[9]
    currentLow = current_btc_Low
    current_btc_High = btc_highs[9]
    currentHigh = current_btc_High
    global btc_chart
    btc_ohlc['date'] = btc_ohlc['date'].dt.strftime('%Y-%m-%d')
    btc_ohlc = btc_ohlc.applymap(str)
    btc_ohlc = btc_ohlc.reindex(index=btc_ohlc.index[::-1])
    btc_chart = btc_ohlc.to_json(orient='records')

    eth_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/ethereum/historical-data/?start=" + yesterday.strftime('%Y%m%d')
                 + "&end=" + time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    eth_market_info['Volume'] = eth_market_info['Volume'].astype('int64')

    eth_market_info['100ma'] = eth_market_info['Close'].rolling(window=100, min_periods=0).mean()

    eth_market_info.reset_index(inplace=True)

    eth_ohlc = eth_market_info.drop(eth_market_info.columns[[5, 6, 7]], axis=1)  # df.columns is zero-based pd.Index
    print(eth_ohlc.head())

    # ltc_ohlc['Date'] = ltc_ohlc['Date'].map(str(ltc_market_info['Date']))
    eth_ohlc = eth_ohlc.rename(columns={'Date': 'date'})
    eth_ohlc = eth_ohlc.rename(columns={'Open': 'open'})
    eth_ohlc = eth_ohlc.rename(columns={'High': 'high'})
    eth_ohlc = eth_ohlc.rename(columns={'Low': 'low'})
    eth_ohlc = eth_ohlc.rename(columns={'Close': 'close'})

    eth_lows = eth_market_info['Low']
    eth_highs = eth_market_info['High']
    current_eth_Low = eth_lows[9]
    currentLow = current_eth_Low
    current_eth_High = eth_highs[9]
    currentHigh = current_eth_High

    global eth_chart
    eth_ohlc['date'] = eth_ohlc['date'].dt.strftime('%Y-%m-%d')
    eth_ohlc = eth_ohlc.applymap(str)
    eth_ohlc = eth_ohlc.reindex(index=eth_ohlc.index[::-1])
    eth_chart = eth_ohlc.to_json(orient='records')

    ltc_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/litecoin/historical-data/?start=" + yesterday.strftime('%Y%m%d')
                 + "&end=" + time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    ltc_market_info['Volume'] = ltc_market_info['Volume'].astype('int64')
    ltc_market_info['100ma'] = ltc_market_info['Close'].rolling(window=100, min_periods=0).mean()
    # resampling
    ltc_market_info.reset_index(inplace=True)
    print(ltc_market_info.head())
    ltc_ohlc = ltc_market_info.drop(ltc_market_info.columns[[5, 6, 7]], axis=1)  # df.columns is zero-based pd.Index
    print(ltc_ohlc.head())

    # ltc_ohlc['Date'] = ltc_ohlc['Date'].map(str(ltc_market_info['Date']))
    ltc_ohlc = ltc_ohlc.rename(columns={'Date': 'date'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Open': 'open'})
    ltc_ohlc = ltc_ohlc.rename(columns={'High': 'high'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Low': 'low'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Close': 'close'})
    # ltc_market_info['Date'] = ltc_market_info['Date'].map(dates.date2num)

    ltc_lows = ltc_market_info['Low']
    ltc_highs = ltc_market_info['High']
    current_ltc_Low = ltc_lows[9]
    currentLow = current_ltc_Low
    current_ltc_High = ltc_highs[9]
    currentHigh = current_ltc_High
    global ltc_chart
    ltc_ohlc['date'] = ltc_ohlc['date'].dt.strftime('%Y-%m-%d')
    ltc_ohlc = ltc_ohlc.applymap(str)
    ltc_ohlc = ltc_ohlc.reindex(index=ltc_ohlc.index[::-1])
    ltc_chart = ltc_ohlc.to_json(orient='records')

    numarraybtc = []
    numarrayltc = []
    numarrayeth = []
    for i in btc_ohlc['close']:
        numarraybtc.append(int(round(float(i))))

    for i in ltc_ohlc['close']:
        numarrayltc.append(int(round(float(i))))

    for i in eth_ohlc['close']:
        numarrayeth.append(int(round(float(i))))

    print(gentrends(numarraybtc))
    print(gentrends(numarrayltc))
    print(gentrends(numarrayeth))


def get_btc_chart():
    global btc_chart
    mlrun()
    return btc_chart


def get_ltc_chart():
    global ltc_chart
    mlrun()
    return ltc_chart


def get_eth_chart():
    global eth_chart
    mlrun()
    return eth_chart


if __name__ == "__main__":
    mlrun()
