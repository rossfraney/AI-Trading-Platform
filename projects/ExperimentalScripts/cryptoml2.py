""" Module for Bitcoina and Ethereum Predictions """
import time
import datetime
from decimal import Decimal
from datetime import date, timedelta
import matplotlib
from keras.models import load_model, Sequential
from keras.layers import Activation, Dense, LSTM, Dropout
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import boto3

matplotlib.use('Agg')

wins = []
loss = []


def get_stats(actual_price, coin_preds):
    i = len(actual_price) - 11  # Window size = 10
    global wins
    global loss

    wins = []
    loss = []

    while i > 0:
        if actual_price[i] < actual_price[i + 1]:
            if coin_preds[i] > actual_price[i]:
                wins.append(actual_price[i + 1] - actual_price[i])
            else:
                loss.append(actual_price[i + 1] - actual_price[i])
        else:
            if actual_price[i] > actual_price[i + 1]:
                if coin_preds[i] > actual_price[i]:
                    loss.append(actual_price[i] - actual_price[i + 1])
                else:
                    wins.append(actual_price[i] - actual_price[i + 1])
        i -= 1

    prof = 0
    for i in wins:
        prof += i
    for i in loss:
        prof -= i

    return prof


def mlrun():
    now = datetime.datetime.now()
    bitcoin_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20130428&end="
                 + time.strftime("%Y%m%d"), flavor='html5lib')[0]
    bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
    bitcoin_market_info.loc[bitcoin_market_info['Volume'] == "-", 'Volume'] = 0
    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')
    bitcoin_market_info['MA'] = bitcoin_market_info['Close'].rolling(window=50).mean()

    eth_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/ethereum/historical-data/?start=20130428&end=" +
                 time.strftime("%Y%m%d"))[0]
    eth_market_info = eth_market_info.assign(Date=pd.to_datetime(eth_market_info['Date']))
    eth_market_info['MA'] = eth_market_info['Close'].rolling(window=50).mean()

    ltc_market_info = \
    pd.read_html("https://coinmarketcap.com/currencies/litecoin/historical-data/?start=20130428&end=" +
                 time.strftime("%Y%m%d"))[0]
    ltc_market_info = ltc_market_info.assign(Date=pd.to_datetime(ltc_market_info['Date']))
    ltc_market_info.loc[ltc_market_info['Volume'] == "-", 'Volume'] = 0
    ltc_market_info['Volume'] = ltc_market_info['Volume'].astype('int64')
    ltc_market_info['MA'] = ltc_market_info['Close'].rolling(window=50).mean()

    bitcoin_market_info.columns = [bitcoin_market_info.columns[0]] + ['bt_' + i for i in
                                                                      bitcoin_market_info.columns[1:]]
    eth_market_info.columns = [eth_market_info.columns[0]] + ['eth_' + i for i in eth_market_info.columns[1:]]
    ltc_market_info.columns = [ltc_market_info.columns[0]] + ['ltc_' + i for i in ltc_market_info.columns[1:]]

    market_info = bitcoin_market_info.merge(eth_market_info, on='Date').merge(ltc_market_info, on='Date')
    market_info = market_info[market_info['Date'] >= '2016-01-01']
    for coins in ['bt_', 'eth_', 'ltc_']:
        kwargs = {coins + 'day_diff': lambda x: (x[coins + 'Close'] - x[coins + 'Open']) / x[coins + 'Open']}
        market_info = market_info.assign(**kwargs)

    split_date = '2017-12-31'

    np.random.seed(666)

    for coins in ['bt_', 'eth_', 'ltc_']:
        kwargs = {coins + 'close_off_high': lambda x: 2 * (x[coins + 'High'] - x[coins + 'Close']) / (
                x[coins + 'High'] - x[coins + 'Low']) - 1,
                  coins + 'volatility': lambda x: (x[coins + 'High'] - x[coins + 'Low']) / (x[coins + 'Open'])}
        market_info = market_info.assign(**kwargs)

    model_data = market_info[['Date'] + [coin + metric for coin in ['bt_', 'eth_', 'ltc_']
                                         for metric in ['Close', 'Volume', 'close_off_high', 'volatility']]]
    model_data = model_data.sort_values(by='Date')
    training_set, test_set = model_data[model_data['Date'] < split_date], model_data[model_data['Date'] >= split_date]
    training_set = training_set.drop('Date', 1)
    test_set = test_set.drop('Date', 1)

    window_len = 10
    norm_cols = [coin + metric for coin in ['bt_', 'eth_', 'ltc_'] for metric in ['Close', 'Volume']]

    LSTM_training_inputs = []
    for i in range(len(training_set) - window_len):
        temp_set = training_set[i:(i + window_len)].copy()
        for col in norm_cols:
            temp_set.loc[:, col] = temp_set[col] / temp_set[col].iloc[0] - 1
        LSTM_training_inputs.append(temp_set)

    LSTM_test_inputs = []
    for i in range(len(test_set) - window_len):
        temp_set = test_set[i:(i + window_len)].copy()
        for col in norm_cols:
            temp_set.loc[:, col] = temp_set[col] / temp_set[col].iloc[0] - 1
        LSTM_test_inputs.append(temp_set)

    LSTM_training_inputs = [np.array(LSTM_training_input) for LSTM_training_input in LSTM_training_inputs]
    LSTM_training_inputs = np.array(LSTM_training_inputs)

    LSTM_test_inputs = [np.array(LSTM_test_inputs) for LSTM_test_inputs in LSTM_test_inputs]
    LSTM_test_inputs = np.array(LSTM_test_inputs)

    eth_model = load_model('eth_model50MA%d.h5')


    ##DrawZoomedTraining##
    from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset

    fig, ax1 = plt.subplots(1, 1)
    ax1.set_xticks([datetime.date(i, j, 1) for i in range(2013, 2019) for j in [1, 5, 9]])
    ax1.set_xticklabels([datetime.date(i, j, 1).strftime('%b %Y') for i in range(2013, 2019) for j in [1, 5, 9]])
    ax1.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
             training_set['eth_Close'][window_len:], label='Actual')
    ax1.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
             ((np.transpose(eth_model.predict(LSTM_training_inputs)) + 1) * training_set['eth_Close'].values[
                                                                            :-window_len])[0],
             label='Predicted')
    ax1.set_title('Training Set: Single Timepoint Prediction')
    ax1.set_ylabel('Ethereum Price ($)', fontsize=12)
    ax1.legend(bbox_to_anchor=(0.15, 1), loc=2, borderaxespad=0., prop={'size': 14})
    ax1.annotate('MAE: %.4f' % np.mean(np.abs((np.transpose(eth_model.predict(LSTM_training_inputs)) + 1) - \
                                              (training_set['eth_Close'].values[window_len:]) / (
                                              training_set['eth_Close'].values[:-window_len]))),
                 xy=(0.75, 0.9), xycoords='axes fraction',
                 xytext=(0.75, 0.9), textcoords='axes fraction')

    # figure inset code taken from http://akuederle.com/matplotlib-zoomed-up-inset
    axins = zoomed_inset_axes(ax1, 3.35, loc=10)  # zoom-factor: 3.35, location: centre
    axins.set_xticks([datetime.date(i, j, 1) for i in range(2013, 2019) for j in [1, 5, 9]])
    axins.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
               training_set['eth_Close'][window_len:], label='Actual')
    axins.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
               ((np.transpose(eth_model.predict(LSTM_training_inputs)) + 1) * training_set['eth_Close'].values[
                                                                              :-window_len])[0],
               label='Predicted')
    axins.set_xlim([datetime.date(2017, 3, 1), datetime.date(2017, 5, 1)])
    axins.set_ylim([10, 60])
    axins.set_xticklabels('')
    mark_inset(ax1, axins, loc1=1, loc2=3, fc="none", ec="0.5")
    ethnum = ((np.transpose(eth_model.predict(LSTM_test_inputs)) + 1) * test_set['eth_Close'].values[:-window_len])
    ethnum = ethnum.flatten()
    ethnum_len = len(ethnum)

    eth_single_Step_pred = ethnum[ethnum_len - 1]
    ethreals = test_set['eth_Close'].values
    ethprof = get_stats(ethreals, ethnum)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('mlpredstats')
    dynamoTable.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'coin': 'eth',
            'preds': str(ethnum),
            'actual': str(ethreals),
            'wins': len(wins),
            'loss': len(loss),
            'prof': str(ethprof)
        }
    )

    dynamoTablePreds = dynamodb.Table('crypto_prediction')
    dynamoTablePreds.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'coin_id': 'eth',
            'pred': Decimal(str(eth_single_Step_pred)),

        })

    fig, ax1 = plt.subplots(1, 1)
    ax1.set_xticks([datetime.date(2017, i + 1, 1) for i in range(12)])
    ax1.set_xticklabels([datetime.date(2017, i + 1, 1).strftime('%b %d %Y') for i in range(12)])
    ax1.plot(model_data[model_data['Date'] >= split_date]['Date'][window_len:].astype(datetime.datetime),
             test_set['eth_Close'][window_len:], label='Actual')
    ax1.plot(model_data[model_data['Date'] >= split_date]['Date'][window_len:].astype(datetime.datetime),
             ((np.transpose(eth_model.predict(LSTM_test_inputs)) + 1) * test_set['eth_Close'].values[:-window_len])[0],
             label='Predicted')
    ax1.annotate('MAE: %.4f' % np.mean(np.abs((np.transpose(eth_model.predict(LSTM_test_inputs)) + 1) - \
                                              (test_set['eth_Close'].values[window_len:]) / (
                                              test_set['eth_Close'].values[:-window_len]))),
                 xy=(0.75, 0.9), xycoords='axes fraction',
                 xytext=(0.75, 0.9), textcoords='axes fraction')
    ax1.set_title('Test Set: Single Timepoint Prediction', fontsize=13)
    ax1.set_ylabel('Ethereum Price ($)', fontsize=12)
    ax1.legend(bbox_to_anchor=(0.1, 1), loc=2, borderaxespad=0., prop={'size': 14})


    np.random.seed(200)
    bt_model = load_model('bt_model50MA%d.h5')

    fig, ax1 = plt.subplots(1, 1)
    ax1.set_xticks([datetime.date(i, j, 1) for i in range(2013, 2019) for j in [1, 5, 9]])
    ax1.set_xticklabels([datetime.date(i, j, 1).strftime('%b %Y') for i in range(2013, 2019) for j in [1, 5, 9]])
    ax1.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
             training_set['bt_Close'][window_len:], label='Actual')
    ax1.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
             ((np.transpose(bt_model.predict(LSTM_training_inputs)) + 1) * training_set['bt_Close'].values[
                                                                           :-window_len])[0],
             label='Predicted')
    ax1.set_title('Training Set: Single Timepoint Prediction')
    ax1.set_ylabel('Bitcoin Price ($)', fontsize=12)
    ax1.annotate('MAE: %.4f' % np.mean(np.abs((np.transpose(bt_model.predict(LSTM_training_inputs)) + 1) - \
                                              (training_set['bt_Close'].values[window_len:]) / (
                                              training_set['bt_Close'].values[:-window_len]))),
                 xy=(0.75, 0.9), xycoords='axes fraction',
                 xytext=(0.75, 0.9), textcoords='axes fraction')
    ax1.legend(bbox_to_anchor=(0.1, 1), loc=2, borderaxespad=0., prop={'size': 14})

    axins = zoomed_inset_axes(ax1, 2.52, loc=10, bbox_to_anchor=(400, 307))  # zoom-factor: 2.52, location: centre
    axins.set_xticks([datetime.date(i, j, 1) for i in range(2013, 2019) for j in [1, 5, 9]])
    axins.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
               training_set['bt_Close'][window_len:], label='Actual')
    axins.plot(model_data[model_data['Date'] < split_date]['Date'][window_len:].astype(datetime.datetime),
               ((np.transpose(bt_model.predict(LSTM_training_inputs)) + 1) * training_set['bt_Close'].values[
                                                                             :-window_len])[0],
               label='Predicted')
    axins.set_xlim([datetime.date(2017, 2, 15), datetime.date(2017, 5, 1)])
    axins.set_ylim([920, 1400])
    axins.set_xticklabels('')
    mark_inset(ax1, axins, loc1=1, loc2=3, fc="none", ec="0.5")

    btcnum = ((np.transpose(bt_model.predict(LSTM_test_inputs)) + 1) * test_set['bt_Close'].values[:-window_len])
    btcnum = btcnum.flatten()
    btcnum_len = len(btcnum)
    btc_single_Step_pred = btcnum[btcnum_len - 1]

    btcreals = test_set['bt_Close'].values
    btcprof = get_stats(btcreals, btcnum)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('mlpredstats')
    dynamoTable.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'coin': 'btc',
            'preds': str(btcnum),
            'actual': str(btcreals),
            'wins': len(wins),
            'loss': len(loss),
            'prof': str(btcprof)
        }
    )

    dynamoTablePreds = dynamodb.Table('crypto_prediction')
    dynamoTablePreds.put_item(
        Item={
            'date': now.strftime("%Y-%m-%d"),
            'coin_id': 'btc',
            'pred': Decimal(str(btc_single_Step_pred)),

        })


mlrun()
