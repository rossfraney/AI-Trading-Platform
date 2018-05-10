""" Scrapes intraday trade stats table every night at midnight and squashes data
into a single row to be inserted into the daily/historical data table. Also wipes
clean the intraday table to be used the next day. """ 

import base64
import datetime
import os
import sys
import io
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

now = datetime.datetime.now()
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
dynamoTable = dynamodb.Table('trade_stats')
dynamoTableDaily = dynamodb.Table('daily_trade_stats')
d = str(now.strftime("%Y-%m-%d"))
try:
	response = dynamoTable.scan()
except ClientError as e:
	print(e.response['Error']['Message'])
else:
    print(response)
    item = response['Items']
    numtrades = 0
    btc = 0
    ltc = 0
    eth = 0
    eur = 0
    gbp = 0
    sizes = 0
    longs = 0
    shorts = 0
    mins = []

    for i in item:
    	#itemArray.append(i)
    	print(i)
    	numtrades = numtrades +1
    	for val in i.values():
    		if val == 'BTC':
    			btc = btc +1
    		if val == 'ETH':
    			eth = eth +1
    		if val == 'LTC':
    			ltc = ltc +1
    		if val == 'GBP':
    			gbp = gbp +1
    		if val == 'EUR':
    			eur = eur +1

    	for key, val in i.items():
    		if(key == 'min'):
    			mins.append(val)
    		if key =='pos':
    			if val == 'Long':
    				longs = longs +1
    			else:
    				shorts = shorts +1 
    		if key == 'size':
    			sizes = sizes + val

    avg_size = (float) (sizes / numtrades)
    trade_nums = {'BTC': btc, 'ETH': eth, 'LTC': ltc, 'EUR': eur, 
    'GBP' : gbp, 'trades_made': numtrades, 
    'longs' : longs, 'shorts': shorts, 'avg_size': avg_size}
    
    dynamoTableDaily.put_item(
    Item = {
        'date' : now.strftime("%Y-%m-%d"),
        'BTC': Decimal(str(btc)), 
        'ETH': Decimal(str(eth)), 
        'LTC': Decimal(str(ltc)), 
        'EUR': Decimal(str(eur)), 
        'GBP' : Decimal(str(gbp)), 
        'trades_made': Decimal(str(numtrades)), 
        'longs' : Decimal(str(longs)), 
        'shorts': Decimal(str(shorts)),
        'avg_size': Decimal(str(avg_size))
    }
   	)
    
    print(mins)
    for i in mins:
    	dynamoTable.delete_item(
    		Key = {
    		'date': now.strftime("%Y-%m-%d"),
    		'min': i
    		}
    	)
