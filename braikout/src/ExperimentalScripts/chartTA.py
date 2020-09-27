import base64
import bitstamp.client
import pandas as pd
import time
import datetime
from PIL import Image
import io
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os

from matplotlib import dates
from matplotlib.finance import candlestick_ohlc



ltc_chart = []
btc_chart = []
eth_chart = []


def mlrun():
    yesterday = datetime.datetime.now() - timedelta(days=60)
    states = " "

    bitcoin_market_info = pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start="+yesterday.strftime('%Y%m%d')
                                   +"&end="+ time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]
    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')
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
    ltc_market_info['100ma'] = ltc_market_info['Close'].rolling(window = 100, min_periods=0).mean()

    # resampling
    ltc_ohlc = ltc_market_info['Close'].resample('1D').ohlc()
    ltc_df_volume = ltc_market_info['Volume'].resample('1D').sum()
    ltc_ohlc.reset_index(inplace=True)
    ltc_market_info.reset_index(inplace=True)
    ltc_ohlc['Date'] = ltc_ohlc['Date'].map(dates.date2num)
    ltc_market_info['Date'] = ltc_market_info['Date'].map(dates.date2num)
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=5, facecolor='#00004d')
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    ax1.xaxis_date()
    candlestick_ohlc(ax1, ltc_market_info.values, width=0.8, colorup='g')
    ax2.fill_between(ltc_df_volume.index.map(dates.date2num), ltc_df_volume.values, 0)
    global ltc_chart
    ltc_chart = ltc_ohlc.to_json(orient='records', lines=True)
    figLtc = plt.gcf()

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
