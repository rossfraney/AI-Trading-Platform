import json

import boto3
from botocore.exceptions import ClientError

from dashboard import CryptoApi
from dashboard.views import DecimalEncoder

import smtplib
from email.mime.text import MIMEText

def check_for_break(ticker):
    prices = CryptoApi.get_prices(str(ticker), "usd")
    coin_resi = ""
    coin_support = ""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('crypto_predictions')
    try:
        response = dynamoTables.get_item(
            Key={
                'coin_id': ticker
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(response)
        item = response['Item']
        print("Get Item Succeeded")
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder))  ############################## change
        jsondata_charts = json.loads(lol)
        coin_resi = float(jsondata_charts['resi'])
        coin_support = float(jsondata_charts['support'])
        if float(prices['last']) > coin_resi:
            return 'Bull'
        else:
            if float(prices['last']) < coin_support:
                return 'Bear'
        return 'NA'

def main():
    alert_dict = {'btc': check_for_break('btc'), 'ltc': check_for_break('ltc'), 'eth': check_for_break('eth')}

    # for key, value in alert_dict.values():
    #     if value == 'Bull':
            #return alert to user thatthere has been a bear break on key
# Create a text/plain message
    msg = MIMEText("There has been a bullish break on "+ str("lol"))
    msg['Subject'] = 'Resistance Broken Alert!'
    msg['From'] = 'Rathnewross@gmail.com'
    msg['To'] = 'Ross.franey3@mail.dcu.ie'

    s = smtplib.SMTP('localhost')
    s.sendmail('Rathnewross@gmail.com', 'Ross.franey3@mail.dcu.ie', msg.as_string())
    s.quit()

if __name__ == '__main__':
    main()