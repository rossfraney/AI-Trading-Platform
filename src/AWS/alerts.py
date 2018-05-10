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
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder))  ############################## change
        jsondata_charts = json.loads(lol)
        token = jsondata_charts['token']
        if value == 'Bear':
            val = "below" 
        else:
            val = "above"
        
    # api key to allow notifications to be pushed to the firebase server
        push_service = FCMNotification(api_key="AAAAHsWsHB4:APA91bGfadwyPWvdbEZK7fAnYv-v2Z7zUxlQKi3nKA1ZGxGNx4hozTWfkMvyFcinayfcym2VG1pdRXDEHG5xUItUAKHmltZSVsvpDxafZqt8zeK9f6KGxdFVuESeZuHCv6bloCU0N-3s")

        registration_id = token

        # main title on notification
        message_title = value + "Price Reached"

        # main message of notification
        message_body = "Price Alert Triggered: " + key + " is " + val + " trigger price."

        # result is to be pushed
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

        return result

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
        lol = (json.dumps(item, indent=4, cls=DecimalEncoder))  ############################## change
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

            #return alert to user thatthere has been a bear break on key

    # Find these values at https://twilio.com/user/account
    # account_sid = "AC7941b1de9b182d0eaeed2ea2ee399801"
    # auth_token = "ac5492614f5693ede40e77df4833a4bb"

    # client = Client(account_sid, auth_token)

    # client.api.account.messages.create(
    #     to="+353861921718",
    #     from_="+353861802622",
    #     body="Hello there!")

if __name__ == '__main__':
    main()