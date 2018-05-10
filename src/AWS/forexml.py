""" Forex Module for predictions """
import base64
import datetime
import os
import io

import boto3
import numpy as np
import pandas as pd
from PIL import Image
from decimal import Decimal
from tradingWithPython import yahooFinance as yf
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier

from sklearn.externals import joblib

now = datetime.datetime.now()
dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('crypto_prediction')
dynamoTableForex = dynamodb.Table('forexstats')

df = pd.DataFrame(yf.getSymbolData("EUR=X", adjust=True))
df = df[['open', 'high', 'low', 'close']]

df.reset_index().assign(
    Date=pd.to_datetime(
        df.reset_index()['Date'])).plot(x='Date', y='close', figsize=(10, 4))

fig_eur_all = plt.gcf()
canvas_eur_all = fig_eur_all.canvas
buf_eur_all, size_eur_all = canvas_eur_all.print_to_buffer()
image_eur_all = Image.frombuffer('RGBA', size_eur_all, buf_eur_all, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_eur_all.save(buffer,'PNG')
graphic_eur_all = buffer.getvalue()
graphic_eur_all = base64.b64encode(graphic_eur_all)
buffer.close()
imgdata = base64.b64decode(graphic_eur_all)
filename = 'images/eur_all.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()

df['return'] = df['close'] - df['close'].shift(1)
return_range = df['return'].max() - df['return'].min()
df['return'] = df['return'] / return_range

df.reset_index().assign(
    Date=pd.to_datetime(
        df.reset_index()['Date'])).plot(x='Date', y='return', figsize=(10, 4))

fig_eur_normalized = plt.gcf()
canvas_eur_normalized = fig_eur_normalized.canvas
buf_eur_normalized, size_eur_normalized = canvas_eur_normalized.print_to_buffer()
image_eur_normalized = Image.frombuffer(
    'RGBA', size_eur_normalized, buf_eur_normalized, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_eur_normalized.save(buffer,'PNG')
graphic_eur_normalized = buffer.getvalue()
graphic_eur_normalized = base64.b64encode(graphic_eur_normalized)
buffer.close()
imgdata = base64.b64decode(graphic_eur_normalized)
filename = 'images/eur_normalized.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()
df['label'] = df['return'].shift(-1)
df['label'] = df['label'].apply(lambda x: 1 if x>0.0 else 0)
df.dropna(inplace=True)
print(df.tail())

df = df.reset_index().assign(Date=pd.to_datetime(df.reset_index()['Date']))

n_features = 100 

train_x = np.array([]).reshape([-1,n_features])
train_y = np.array([]).reshape([-1,1])
for index, row in df.iterrows():
    i = df.index.get_loc(index)
    if i<n_features:
        continue

    _x = np.array(df[i-n_features+1:i+1]['return']).T.reshape([1, -1])
    _y = df.loc[i]['label']
    train_x = np.vstack((train_x, _x))
    train_y = np.vstack((train_y, _y))
train_y = train_y.reshape([-1])
print(train_x.shape)
print(train_y.shape)
print('%% of Class0 : %f' % (np.count_nonzero(train_y == 0)/float(len(train_y))))
print('%% of Class1 : %f' % (np.count_nonzero(train_y == 1)/float(len(train_y))))

# Define Model and fit
# Here we use 95% of data for training, and last 5% for testing

clf = joblib.load('eur_model.pk2')#GradientBoostingClassifier(random_state=0, learning_rate=0.01, n_estimators=10000)
#clf = GradientBoostingClassifier(random_state=0, learning_rate=0.01, n_estimators=10000)

train_len = int(len(train_x)*0.95)
#clf.fit(train_x[:train_len], train_y[:train_len])
#joblib.dump(clf, 'eur_model.pk2')


accuracy = clf.score(train_x[train_len:], train_y[train_len:])
print('Testing Accuracy: %f' % accuracy)


# Predict test data

pred = clf.predict(train_x[train_len:])
euro_pred = pred[len(train_x[train_len:]) -1]

dynamoTable.put_item(
    Item = {
        'coin_id' : 'eur',
        'date'  : now.strftime("%Y-%m-%d"),
        'pred' : Decimal(str(euro_pred)),
        'prev' : 'N/A'
    }
)

# Calculate equity..

starting_eq  = 10000.0
z = 0.0


df_trade = pd.DataFrame(train_x[train_len:,-1], columns=['return'])
df_trade['label']  = train_y[train_len:]
df_trade['pred']   = pred
df_trade['won']    = df_trade['label'] == df_trade['pred']
df_trade['return'] = df_trade['return'].shift(-1) * return_range
df_trade.drop(df_trade.index[len(df_trade)-1], inplace=True)

def get_stats(row):
    """ get result of running backtest with capital """
    if row['won']:
        return abs(row['return'])*starting_eq - z
    else:
        return -abs(row['return'])*starting_eq - z


df_trade['prof'] = df_trade.apply(lambda row: get_stats(row), axis=1)
df_trade['equity'] = df_trade['prof'].cumsum()

print(df_trade.tail())
df_trade.plot(y='equity', figsize=(10,4), title='$10k Backtest')
plt.xlabel('Trades')
plt.ylabel('Equity (USD)')
for r in df_trade.iterrows():
    if r[1]['won']:
        plt.axvline(x=r[0], linewidth=0.5, alpha=0.8, color='g')
    else:
        plt.axvline(x=r[0], linewidth=0.5, alpha=0.8, color='r')
fig_eur = plt.gcf()
canvas_eur = fig_eur.canvas
buf_eur, size_eur = canvas_eur.print_to_buffer()
image_eur = Image.frombuffer('RGBA', size_eur, buf_eur, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_eur.save(buffer,'PNG')
graphic_eur = buffer.getvalue()
graphic_eur = base64.b64encode(graphic_eur)
buffer.close()
imgdata = base64.b64decode(graphic_eur)
filename = 'images/eur_backtest.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()


eur_n_win_trades = float(df_trade[df_trade['prof']>0.0]['prof'].count())
eur_n_los_trades = float(df_trade[df_trade['prof']<0.0]['prof'].count())
eur_net_profit = str("Net Profit            : $%.2f" % df_trade.tail(1)['equity'])
eur_num_winning_trades = str("Number Winning Trades : %d" % eur_n_win_trades)
eur_num_loosing_trades = ("Number Losing Trades  : %d" % eur_n_los_trades)
eur_percentage_profitable = str("Percent Profitable    : %.2f%%" % (100*eur_n_win_trades/(eur_n_win_trades + eur_n_los_trades)))
eur_avg_win_trade = str("Avg Win Trade         : $%.3f" % df_trade[df_trade['prof']>0.0]['prof'].mean())
eur_avg_loss_trade = str("Avg Loss Trade         : $%.3f" % df_trade[df_trade['prof']<0.0]['prof'].mean())
eur_largest_win_trade = str("Largest Win Trade     : $%.3f" % df_trade[df_trade['prof']>0.0]['prof'].max())
eur_largest_loss_trade = str("Largest Loss Trade     : $%.3f" % df_trade[df_trade['prof']<0.0]['prof'].min())
eur_profit_factor = str("Profit Factor         : %.2f" % abs(df_trade[df_trade['prof']>0.0]['prof'].sum()/df_trade[df_trade['prof']<0.0]['prof'].sum()))

dynamoTableForex.put_item(
    Item = {
        'date'  : now.strftime("%Y-%m-%d"),
        'coin_id' : 'eur',
        'win_trades' : eur_num_winning_trades,
        'loss_trades' : eur_num_loosing_trades,
        'net_prof': eur_net_profit,
        'percent_profit': eur_percentage_profitable,
        'avg_win_trade': eur_avg_win_trade,
        'avg_loss_trade': eur_avg_loss_trade,
        'largest_win_trade': eur_largest_win_trade,
        'largest_loss_trade': eur_largest_loss_trade,
        'profit_factor': eur_profit_factor
    }
)


df = pd.DataFrame(yf.getSymbolData("GBP=X", adjust=True))
df = df[['open', 'high', 'low', 'close']]

print(df.tail())

df.reset_index().assign(
    Date=pd.to_datetime(df.reset_index()['Date'])).plot(x='Date', y='close', figsize=(10,4))

fig_gbp_all = plt.gcf()
canvas_gbp_all = fig_gbp_all.canvas
buf_gbp_all, size_gbp_all = canvas_gbp_all.print_to_buffer()
image_gbp_all = Image.frombuffer('RGBA', size_gbp_all, buf_gbp_all, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_gbp_all.save(buffer,'PNG')
graphic_gbp_all = buffer.getvalue()
graphic_gbp_all = base64.b64encode(graphic_gbp_all)
buffer.close()
imgdata = base64.b64decode(graphic_gbp_all)
filename = 'images/gbp_all.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()

df['return'] = df['close'] - df['close'].shift(1)
return_range = df['return'].max() - df['return'].min()
df['return'] = df['return'] / return_range

df.reset_index().assign(
    Date=pd.to_datetime(
        df.reset_index()['Date'])).plot(x='Date', y='return', figsize=(10, 4))

fig_eur_normalized = plt.gcf()
canvas_eur_normalized = fig_eur_normalized.canvas
buf_eur_normalized, size_eur_normalized = canvas_eur_normalized.print_to_buffer()
image_eur_normalized = Image.frombuffer(
    'RGBA', size_eur_normalized, buf_eur_normalized, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_eur_normalized.save(buffer,'PNG')
graphic_eur_normalized = buffer.getvalue()
graphic_eur_normalized = base64.b64encode(graphic_eur_normalized)
buffer.close()
imgdata = base64.b64decode(graphic_eur_normalized)
filename = 'images/eur_normalized.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()

df['label'] = df['return'].shift(-1)
df['label'] = df['label'].apply(lambda x: 1 if x>0.0 else 0)
df.dropna(inplace=True)
print(df.tail())

df = df.reset_index().assign(Date=pd.to_datetime(df.reset_index()['Date']))

n_features = 100 

train_x = np.array([]).reshape([-1,n_features])
train_y = np.array([]).reshape([-1,1])
for index, row in df.iterrows():
    i = df.index.get_loc(index)
    if i<n_features:
        continue

    _x = np.array(df[i-n_features+1:i+1]['return']).T.reshape([1, -1])
    _y = df.loc[i]['label']
    train_x = np.vstack((train_x, _x))
    train_y = np.vstack((train_y, _y))
train_y = train_y.reshape([-1])
print(train_x.shape)
print(train_y.shape)
print('%% of Class0 : %f' % (np.count_nonzero(train_y == 0)/float(len(train_y))))
print('%% of Class1 : %f' % (np.count_nonzero(train_y == 1)/float(len(train_y))))


# clf = clf = joblib.load('gbp_model.pk1')
GradientBoostingClassifier(random_state=0, learning_rate=0.01, n_estimators=10000)
clf = GradientBoostingClassifier(random_state=0, learning_rate=0.01, n_estimators=10000)

train_len = int(len(train_x)*0.95)
clf.fit(train_x[:train_len], train_y[:train_len])
joblib.dump(clf, 'gbp_model.pk')


accuracy = clf.score(train_x[train_len:], train_y[train_len:])
print('Testing Accuracy: %f' % accuracy)

pred = clf.predict(train_x[train_len:])
gbp_pred = pred[len(train_x[train_len:]) -1]

dynamoTable.put_item(
    Item = {
        'coin_id' : 'gbp',
        'date'  : now.strftime("%Y-%m-%d"),
        'pred' : Decimal(str(gbp_pred)),
        'prev' : 'N/A'
    }
)

starting_eq  = 10000.0
z = 0.0

df_trade = pd.DataFrame(train_x[train_len:,-1], columns=['return'])
df_trade['label'] = train_y[train_len:]
df_trade['pred'] = pred
df_trade['won'] = df_trade['label'] == df_trade['pred']
df_trade['return'] = df_trade['return'].shift(-1) * return_range
df_trade.drop(df_trade.index[len(df_trade)-1], inplace=True)


df_trade['prof'] = df_trade.apply(lambda row: get_stats(row), axis=1)
df_trade['equity'] = df_trade['prof'].cumsum()

print(df_trade.tail())
df_trade.plot(y='equity', figsize=(10, 4), title='$10k Backtest')
plt.xlabel('Trades')
plt.ylabel('Equity (USD)')
for r in df_trade.iterrows():
    if r[1]['won']:
        plt.axvline(x=r[0], linewidth=0.5, alpha=0.8, color='g')
    else:
        plt.axvline(x=r[0], linewidth=0.5, alpha=0.8, color='r')
fig_gbp = plt.gcf()
canvas_gbp = fig_gbp.canvas
buf_gbp, size_gbp = canvas_gbp.print_to_buffer()
image_gbp = Image.frombuffer('RGBA', size_gbp, buf_gbp, 'raw', 'RGBA', 0, 1)
buffer = io.BytesIO()
image_gbp.save(buffer,'PNG')
graphic_gbp = buffer.getvalue()
graphic_gbp = base64.b64encode(graphic_gbp)
buffer.close()
imgdata = base64.b64decode(graphic_gbp)
filename = 'images/gbp_backtest.png'
with open(filename, 'wb') as f:
    f.write(imgdata)
f.close()


# # Calculate summary of trades
#
gbp_n_win_trades = float(df_trade[df_trade['prof']>0.0]['prof'].count())
gbp_n_los_trades = float(df_trade[df_trade['prof']<0.0]['prof'].count())
gbp_net_profit = str("Net Profit            : $%.2f" % df_trade.tail(1)['equity'])
gbp_num_winning_trades = str("Number Winning Trades : %d" % gbp_n_win_trades)
gbp_num_loosing_trades = ("Number Losing Trades  : %d" % gbp_n_los_trades)
gbp_percentage_profitable = str("Percent Profitable    : %.2f%%" % (100*gbp_n_win_trades/(gbp_n_win_trades + gbp_n_los_trades)))
gbp_avg_win_trade = str("Avg Win Trade         : $%.3f" % df_trade[df_trade['prof']>0.0]['prof'].mean())
gbp_avg_loss_trade = str("Avg Loss Trade         : $%.3f" % df_trade[df_trade['prof']<0.0]['prof'].mean())
gbp_largest_win_trade = str("Largest Win Trade     : $%.3f" % df_trade[df_trade['prof']>0.0]['prof'].max())
gbp_largest_loss_trade = str("Largest Loss Trade     : $%.3f" % df_trade[df_trade['prof']<0.0]['prof'].min())
gbp_profit_factor = str("Profit Factor         : %.2f" % abs(df_trade[df_trade['prof']>0.0]['prof'].sum()/df_trade[df_trade['prof']<0.0]['prof'].sum()))

print(gbp_n_win_trades)
print(gbp_n_los_trades)
print(gbp_net_profit)
print(gbp_num_winning_trades)
print(gbp_num_loosing_trades)
print(gbp_percentage_profitable)
print(gbp_avg_win_trade)
print(gbp_avg_loss_trade)
print(gbp_largest_win_trade)
print(gbp_largest_loss_trade)
print(gbp_profit_factor)


dynamoTableForex.put_item(
    Item = {
        'date'  : now.strftime("%Y-%m-%d"),
        'coin_id' : 'gbp',
        'win_trades' : gbp_num_winning_trades,
        'loss_trades' : gbp_num_loosing_trades,
        'net_prof': gbp_net_profit,
        'percent_profit': gbp_percentage_profitable,
        'avg_win_trade': gbp_avg_win_trade,
        'avg_loss_trade': gbp_avg_loss_trade,
        'largest_win_trade': gbp_largest_win_trade,
        'largest_loss_trade': gbp_largest_loss_trade,
        'profit_factor': gbp_profit_factor
    }
)

os.system('aws s3 sync /home/ubuntu/images s3://braikoutpredictions/'
          'Images --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers')

