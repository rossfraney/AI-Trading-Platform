from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response


class ChartData(UpdateAPIView):

    # TODO Refactor next
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
        senti_labels = []
        pred_labels = []
        senti_values = []
        predicted_change = []

        for coin in all_coins:
            senti_labels.append(str(coin.ticker))
            if coin.is_favorite and coin.ticker != 'EUR':
                pred_labels.append(str(coin.ticker))
            senti_values.append(float(coin.sentiment_score))
            a = coin.predictions
            c = coin.current_price
            if a == c:
                if coin.is_favorite and coin.ticker != 'EUR':
                    predicted_change.append(0)
            price_check = (abs(float((a - c) / c))) * 100
            if a > c:
                current_biggest_diff = price_check
            else:
                current_biggest_diff = -1 * price_check
            if coin.is_favorite and coin.ticker != 'EUR':
                predicted_change.append(current_biggest_diff)

        length = len(labels)
        i = 0
        while i < length:
            if labels[i] == 'usd':
                i = i + 1
            else:
                prices = CryptoApi.get_prices(labels[i], "usd")
                last_price = prices['last']
                value[i] = float(value[i]) * float(last_price)
                i = i + 1
        data = {
            "labels": labels,
            "senti_labels": senti_labels,
            "pred_labels": pred_labels,
            "default": value,
            "senti_default": senti_values,
            "predicted_change": predicted_change,
        }
        return Response(data)