import json
from twilio.rest import Client
import boto3
from botocore.exceptions import ClientError
import bitstamp.client
import decimal

from pyfcm import FCMNotification

# Notifications to the App via firebase server
def notify(key, value):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    dynamoTables = dynamodb.Table('alerts')
    val = " "
    try:
        response = dynamoTables.get_item(
            Key={
                'coin_id': "tokenId"
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(response)
        item = response['Item']
        print("Get Item Succeeded")
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder)) 
        jsondata_charts = json.loads(lol)
        token = jsondata_charts['token']
        if value == 'Bear':
            val = "below" 
        else:
            val = "above"
        
#       push_service = FCMNotification(api_key="")

        registration_id = token
        message_title = value + "Price Reached"
        message_body = "Price Alert Triggered: " + key + " is " + val + " trigger price."

        return push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def check_for_break(ticker):
    public_client = bitstamp.client.Public()

    prices = public_client.ticker('btc', 'usd')['last']
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
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder)) 
        jsondata_charts = json.loads(lol)
        coin_resi = float(jsondata_charts['resi'])
        coin_support = float(jsondata_charts['support'])
        if float(prices) > coin_resi:
            return 'Bull'
        else:
            if float(prices) < coin_support:
                return 'Bear'
        return 'NA'

def main():
    btc_state = check_for_break('btc')
    eth_state = check_for_break('eth')
    ltc_state = check_for_break('ltc')
    alert_dict = {'btc': btc_state, 'eth': eth_state, 'ltc': ltc_state}

    for key, value in alert_dict.items():
        if value == 'Bull':
            notify(key, value)
        if value == 'Bear': 
            notify(key, value)

if __name__ == '__main__':
    main()
