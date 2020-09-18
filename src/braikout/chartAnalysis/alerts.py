import json

import boto3
import smtplib

from botocore.exceptions import ClientError
from dashboard import CryptoApi
from dashboard.views import DecimalEncoder
from email.mime.text import MIMEText


def check_for_break(ticker):
    prices = CryptoApi.get_prices(str(ticker), "usd")
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
        item = response['Item']
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder))
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
    msg = MIMEText("There has been a bullish break on "+ str("lol"))
    msg['Subject'] = 'Resistance Broken Alert!'
    msg['From'] = 'Rathnewross@gmail.com'
    msg['To'] = 'Ross.franey3@mail.dcu.ie'

    s = smtplib.SMTP('localhost')
    s.sendmail('Rathnewross@gmail.com', 'Ross.franey3@mail.dcu.ie', msg.as_string())
    s.quit()


if __name__ == '__main__':
    main()