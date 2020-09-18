import pandas as pd
import time
import datetime
from datetime import date, timedelta

ltc_chart = []
btc_chart = []
eth_chart = []


def mlrun():

    yesterday = datetime.datetime.now() - timedelta(days=60)

    bitcoin_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=" + yesterday.strftime('%Y%m%d')
                 + "&end=" + time.strftime("%Y%m%d"), flavor='html5lib', parse_dates=True, index_col=0)[0]

    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')

    bitcoin_market_info['100ma'] = bitcoin_market_info['Close'].rolling(window=100, min_periods=0).mean()

    bitcoin_market_info.reset_index(inplace=True)
    btc_ohlc = bitcoin_market_info.drop(bitcoin_market_info.columns[[5, 6, 7]],
                                        axis=1)  # df.columns is zero-based pd.Index

    btc_ohlc = btc_ohlc.rename(columns={'Date': 'date'})
    btc_ohlc = btc_ohlc.rename(columns={'Open': 'open'})
    btc_ohlc = btc_ohlc.rename(columns={'High': 'high'})
    btc_ohlc = btc_ohlc.rename(columns={'Low': 'low'})
    btc_ohlc = btc_ohlc.rename(columns={'Close': 'close'})

    ##Chart analysis
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

    eth_ohlc = eth_ohlc.rename(columns={'Date': 'date'})
    eth_ohlc = eth_ohlc.rename(columns={'Open': 'open'})
    eth_ohlc = eth_ohlc.rename(columns={'High': 'high'})
    eth_ohlc = eth_ohlc.rename(columns={'Low': 'low'})
    eth_ohlc = eth_ohlc.rename(columns={'Close': 'close'})

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
    ltc_ohlc = ltc_market_info.drop(ltc_market_info.columns[[5, 6, 7]], axis=1)  # df.columns is zero-based pd.Index

    ltc_ohlc = ltc_ohlc.rename(columns={'Date': 'date'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Open': 'open'})
    ltc_ohlc = ltc_ohlc.rename(columns={'High': 'high'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Low': 'low'})
    ltc_ohlc = ltc_ohlc.rename(columns={'Close': 'close'})

    global ltc_chart
    ltc_ohlc['date'] = ltc_ohlc['date'].dt.strftime('%Y-%m-%d')
    ltc_ohlc = ltc_ohlc.applymap(str)
    ltc_ohlc = ltc_ohlc.reindex(index=ltc_ohlc.index[::-1])
    ltc_chart = ltc_ohlc.to_json(orient='records')


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
