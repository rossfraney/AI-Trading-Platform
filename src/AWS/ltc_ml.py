import delta as delta
import matplotlib
matplotlib.use('Agg')

import base64
import paramiko

from keras.models import load_model, Sequential
from keras.layers import Activation, Dense, LSTM, Dropout

from sklearn import datasets
from sklearn import svm
import pandas as pd
import time
import seaborn as sns
import datetime
import numpy as np
import sys
from PIL import Image
import io
import matplotlib.pyplot as plt
import boto3
from decimal import Decimal
from datetime import date, timedelta
import os

wins = []
loss = []

def get_stats(actual_price, coin_preds):
    i = len(actual_price) - 11 # Window size = 10
    global wins
    global loss

    wins = []
    loss = []
    correctflag = " "
    while i > 0:
        if actual_price[i] < actual_price[i+1]:
            if coin_preds[i] > actual_price[i]:
                correctflag = "Correct Direction"
                wins.append(actual_price[i+1] - actual_price[i])
            else:
                correctflag = "Incorrect Direction"
                loss.append(actual_price[i+1] - actual_price[i])
        else:
            if actual_price[i] > actual_price[i+1]:
                if coin_preds[i] > actual_price[i]:
                    correctflag = "Incorrect Direction"
                    loss.append(actual_price[i] - actual_price[i+1])
                else:
                    correctflag = "Correct Direction"
                    wins.append(actual_price[i] - actual_price[i+1])
        i -= 1
        print("Day = " + str(i) + ":  REAL:  " + str(actual_price[i]) + ",   PRED:  " + str(round(coin_preds[i], 2)) + "      .....    " + correctflag)

    prof = 0
    for i in wins:
        prof = prof+i
    for i in loss:
        prof = prof-i

    print(str(loss))
    return(prof)


def mlrun():
    """ Runs prediction on litecoin model and when comments removed builds new model """

    now = datetime.datetime.now()
    yesterday = date.today() - timedelta(1)
    from keras.models import load_model
    bitcoin_market_info = pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20130428&end="
                                       + time.strftime("%Y%m%d"), flavor='html5lib')[0]
    bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
    bitcoin_market_info.loc[bitcoin_market_info['Volume'] == "-", 'Volume'] = 0
    bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')
    bitcoin_market_info = bitcoin_market_info.reindex(index=bitcoin_market_info.index[::-1])
    bitcoin_market_info['MA'] = bitcoin_market_info['Close'].rolling(window = 10).mean()
    bitcoin_market_info = bitcoin_market_info.reindex(index=bitcoin_market_info.index[::-1])
    bitcoin_market_info['Return'] = bitcoin_market_info['Close'].shift(1)
    return_range = bitcoin_market_info['Return'].max() - bitcoin_market_info['Return'].min()
    bitcoin_market_info['Return'] = bitcoin_market_info['Return'] / return_range

    eth_market_info = pd.read_html("https://coinmarketcap.com/currencies/ethereum/historical-data/?start=20130428&end=" +
                                   time.strftime("%Y%m%d"))[0]
    eth_market_info = eth_market_info.assign(Date=pd.to_datetime(eth_market_info['Date']))
    eth_prev_close = eth_market_info.loc[[0], 'Close'].values[0] ## gets previous close for the DB to assess performance
    eth_market_info = eth_market_info.reindex(index=eth_market_info.index[::-1])
    eth_market_info['MA'] = eth_market_info['Close'].rolling(window = 10).mean()
    eth_market_info = eth_market_info.reindex(index=eth_market_info.index[::-1])
    eth_market_info['Return'] = eth_market_info['Close'].shift(1)
    return_range = eth_market_info['Return'].max() - eth_market_info['Return'].min()
    eth_market_info['Return'] = eth_market_info['Return'] / return_range


    ltc_market_info = pd.read_html("https://coinmarketcap.com/currencies/litecoin/historical-data/?start=20130428&end=" +
                                   time.strftime("%Y%m%d"))[0]
    ltc_market_info = ltc_market_info.assign(Date=pd.to_datetime(ltc_market_info['Date']))
    ltc_market_info.loc[ltc_market_info['Volume'] == "-", 'Volume'] = 0
    ltc_market_info['Volume'] = ltc_market_info['Volume'].astype('int64')
    ltc_market_info = ltc_market_info.reindex(index=ltc_market_info.index[::-1])
    ltc_market_info['MA'] = ltc_market_info['Close'].rolling(window = 10).mean()
    ltc_market_info = ltc_market_info.reindex(index=ltc_market_info.index[::-1])
    ltc_prev_close = ltc_market_info.loc[[0], 'Close'].values[0] ## gets previous close for the DB to assess performance
    ltc_market_info['Return'] = ltc_market_info['Close'].shift(1)
    return_range = ltc_market_info['Return'].max() - ltc_market_info['Return'].min()
    ltc_market_info['Return'] = ltc_market_info['Return'] / return_range

    bitcoin_market_info.columns = [bitcoin_market_info.columns[0]] + ['bt_' + i for i in bitcoin_market_info.columns[1:]]
    eth_market_info.columns = [eth_market_info.columns[0]] + ['eth_' + i for i in eth_market_info.columns[1:]]
    ltc_market_info.columns = [ltc_market_info.columns[0]] + ['ltc_' + i for i in ltc_market_info.columns[1:]]

    market_info = bitcoin_market_info.merge(eth_market_info, on='Date').merge(ltc_market_info, on='Date')
    market_info = market_info[market_info['Date'] >= '2016-01-01'] 
    for coins in ['bt_', 'eth_', 'ltc_']:
        kwargs = {coins + 'day_diff': lambda x: (x[coins + 'Close'] - x[coins + 'Open']) / x[coins + 'Open']}
        market_info = market_info.assign(**kwargs)
    print(market_info.head())

    split_date = '2017-12-31'

    np.random.seed(666)
    bt_r_walk_mean, bt_r_walk_sd = np.mean(market_info[market_info['Date'] < split_date]['bt_day_diff'].values), \
                                   np.std(market_info[market_info['Date'] < split_date]['bt_day_diff'].values)
    bt_random_steps = np.random.normal(bt_r_walk_mean, bt_r_walk_sd,
                                       (max(market_info['Date']).to_pydatetime() - datetime.datetime.strptime(split_date,
                                                                                                              '%Y-%m-%d')).days + 1)
    eth_r_walk_mean, eth_r_walk_sd = np.mean(market_info[market_info['Date'] < split_date]['eth_day_diff'].values), \
                                     np.std(market_info[market_info['Date'] < split_date]['eth_day_diff'].values)
    eth_random_steps = np.random.normal(eth_r_walk_mean, eth_r_walk_sd,
                                        (max(market_info['Date']).to_pydatetime() - datetime.datetime.strptime(split_date,
                                                                                                               '%Y-%m-%d')).days + 1)
    ltc_r_walk_mean, ltc_r_walk_sd = np.mean(market_info[market_info['Date'] < split_date]['ltc_day_diff'].values), \
                                     np.std(market_info[market_info['Date'] < split_date]['ltc_day_diff'].values)
    ltc_random_steps = np.random.normal(ltc_r_walk_mean, ltc_r_walk_sd,
                                        (max(market_info['Date']).to_pydatetime() - datetime.datetime.strptime(split_date,
                                                                                                               '%Y-%m-%d')).days + 1)

    

    for coins in ['bt_', 'eth_', 'ltc_']:
        kwargs = {coins + 'close_off_high': lambda x: 2 * (x[coins + 'High'] - x[coins + 'Close']) / (
            x[coins + 'High'] - x[coins + 'Low']) - 1,
                  coins + 'volatility': lambda x: (x[coins + 'High'] - x[coins + 'Low']) / (x[coins + 'Open'])}
        market_info = market_info.assign(**kwargs)

    model_data = market_info[['Date'] + [coin + metric for coin in ['bt_', 'eth_', 'ltc_']
                                         for metric in ['Close', 'Volume', 'close_off_high', 'volatility', 'MA', 'Return']]]
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
    ETH_training_outputs = (training_set['eth_Close'][window_len:].values / training_set['eth_Close'][
                                                                            :-window_len].values) - 1
    BTC_training_outputs = (training_set['bt_Close'][window_len:].values / training_set['bt_Close'][
                                                                           :-window_len].values) - 1
    LTC_training_outputs = (training_set['ltc_Close'][window_len:].values / training_set['ltc_Close'][
                                                                            :-window_len].values) - 1

    LSTM_test_inputs = []
    for i in range(len(test_set) - window_len):
        temp_set = test_set[i:(i + window_len)].copy()
        for col in norm_cols:
            temp_set.loc[:, col] = temp_set[col] / temp_set[col].iloc[0] - 1
        LSTM_test_inputs.append(temp_set)
    ETH_test_outputs = (test_set['eth_Close'][window_len:].values / test_set['eth_Close'][:-window_len].values) - 1
    BTC_test_outputs = (test_set['bt_Close'][window_len:].values / test_set['bt_Close'][:-window_len].values) - 1
    LTC_test_outputs = (test_set['ltc_Close'][window_len:].values / test_set['ltc_Close'][:-window_len].values) - 1

    LSTM_training_inputs = [np.array(LSTM_training_input) for LSTM_training_input in LSTM_training_inputs]
    LSTM_training_inputs = np.array(LSTM_training_inputs)

    LSTM_test_inputs = [np.array(LSTM_test_inputs) for LSTM_test_inputs in LSTM_test_inputs]
    LSTM_test_inputs = np.array(LSTM_test_inputs)


    def build_model(inputs, output_size, neurons, activ_func="linear",
                    dropout=0.25, loss="mae", optimizer="adam"):
        model = Sequential()

        model.add(LSTM(neurons, input_shape=(inputs.shape[1], inputs.shape[2])))
        model.add(Dropout(dropout))
        model.add(Dense(units=output_size))
        model.add(Activation(activ_func))

        model.compile(loss=loss, optimizer=optimizer)
        return model

    # np.random.seed(205)
    # ltc_model = build_model(LSTM_training_inputs, output_size=1, neurons=20)
    # #model output is next price normalised to 10th previous closing price
    # LTC_training_outputs = (training_set['ltc_Close'][window_len:].values/training_set['ltc_Close'][:-window_len].values)-1
    # ltc_history = ltc_model.fit(LSTM_training_inputs, LTC_training_outputs,
    #                             epochs=50, batch_size=1, verbose=2, shuffle=True)
    # ltc_model.save('ltc_model%d2nd.h5')
    ltc_model = load_model('ltc_model%d2nd.h5')

    # fig, ax1 = plt.subplots(1,1)
    # ax1.plot(ltc_history.epoch, ltc_history.history['loss'])
    # ax1.set_title('Training Error')
    # if ltc_model.loss == 'mae':
    #     ax1.set_ylabel('Mean Absolute Error (MAE)',fontsize=12)
    # # just in case you decided to change the model loss calculation
    # else:
    #     ax1.set_ylabel('Model Loss',fontsize=12)
    # ax1.set_xlabel('# Epochs',fontsize=12)
    # ltc_mae_fig = plt.gcf()

    ltc_single_step_training = plt.gcf()
    # plt.show()
    ltcnum = ((np.transpose(ltc_model.predict(LSTM_test_inputs))+1) * test_set['ltc_Close'].values[:-window_len])
    ltcnum = ltcnum.flatten()
    ltcnum_len = len(ltcnum)
    ltc_single_Step_pred = ltcnum[ltcnum_len-1] #TODO
    print("PRED =========" + str(ltc_single_Step_pred))
    print("ETHUNM =========== " + str(ltcnum))
    print("REAL =========" + str(test_set['ltc_Close'].values))
    ltcreals = test_set['ltc_Close'].values
    realresltc = test_set['ltc_Close']
    print(len(realresltc))
    ltcprof = get_stats(ltcreals, ltcnum)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTable = dynamodb.Table('mlpredstats')
    dynamoTable.put_item(
        Item = {
            'date': now.strftime("%Y-%m-%d"),
            'coin': 'ltc',
            'preds': str(ltcnum),
            'actual': str(ltcreals),
            'wins' : len(wins),
            'loss': len(loss),
            'prof': str(ltcprof)
        }
    )

    dynamoTablePreds = dynamodb.Table('crypto_prediction')
    dynamoTablePreds.put_item(
    Item = {
        'date'  : now.strftime("%Y-%m-%d"),
        'coin_id' : 'ltc', 
        'pred' : Decimal(str(ltc_single_Step_pred)),

    })


mlrun()
