import json
import requests


def get_coin_price(coin_name):
    """
    Helper for getting coin price for the braikout module

    :param coin_name: Name of coin to get from Bittrex API
    :type coin_name: str

    :return: Price data of coin
    :rtype: dict
    """
    url = "https://bittrex.com/api/v1.1/public/getticker?market=USDT-{}".format(coin_name)
    data = requests.get(url).json()

    return json.dumps({
        coin_name: data.get("result").get("Last")
    })
