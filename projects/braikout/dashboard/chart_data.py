from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from projects.braikout.dashboard import CryptoApi
from projects.braikout.dashboard.models import CoinPrices


class ChartData(UpdateAPIView):

    def get(self, request, format=None):
        """
        Returns data from view to Ajax function
        for visual representation

        :param request: Django request
        :type request: request
        :param format: Format of charts
        :type format: str

        :return: REST Response of chart data
        """

        all_coins = CoinPrices.objects.all()
        wallet = CryptoApi.get_balance_eq()
        labels = list(wallet.keys())
        value = list(wallet.values())

        senti_labels = [str(coin.ticker) for coin in all_coins]
        pred_labels = [str(coin.ticker) for coin in all_coins if coin.is_favorite and coin.ticker != 'EUR']
        senti_values = [float(coin.sentiment_score) for coin in all_coins]
        predicted_change = []

        for coin in all_coins:
            if coin.predictions == coin.current_price and coin.is_favorite and coin.ticker != 'EUR':
                predicted_change.append(0)
            price_check = (abs(float((coin.predictions - coin.current_price) / coin.current_price))) * 100
            current_biggest_diff = price_check if coin.predictions > coin.current_price else -1 * price_check
            if coin.is_favorite and coin.ticker != 'EUR':
                predicted_change.append(current_biggest_diff)

        for i in range(len(labels)):
            if labels[i] != 'usd':
                last_price = CryptoApi.get_prices(labels[i], "usd")['last']
                value[i] = float(value[i]) * float(last_price)

        data = {
            "labels": labels,
            "senti_labels": senti_labels,
            "pred_labels": pred_labels,
            "default": value,
            "senti_default": senti_values,
            "predicted_change": predicted_change,
        }
        return Response(data)