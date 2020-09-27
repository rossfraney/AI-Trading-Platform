import json

import boto3
from django.test import TestCase

from braikout.forms import BuyForm
from chartAnalysis.chartTA import get_btc_chart
from dashboard.ForexApi import get_pos
from machinelearning.views import get_stats
from sentiment.Scraper import get_tweet_sentiment, analyze_tweets_numerical
from .models import CoinPrices


def create_coin(pk, ticker, name, current_price="000", coin_logo="http://www.test.com/test.jpg",
                predictions="111", sentiment_score="20.5", trend="bullish"):
    """ Create a coin test """
    return CoinPrices.objects.create(ticker=ticker, name=name, current_price=current_price,
                                     coin_logo=coin_logo, predictions=predictions,
                                     sentiment_score=sentiment_score, trend=trend,
                                     is_favorite=True, pk=pk)


class BraikoutTest(TestCase):
    """ Tests for braikout view """

    def test_braikout_page(self):
        """ Checks for correct behaviour of main login page """
        url = '/braikout/logout/'
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 200)


class DashboardTest(TestCase):
    """ Tests for dashboard view """

    def test_dashboard_page(self):
        """ Checks for correct behaviour of main dashboard page """
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        ltc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        eth_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        eur_coin = create_coin(ticker='eur', name='euro', pk=4)
        url = '/'
        url_alerts = '/alerts/'
        url_ajax = '/api/chart/data/'
        resp = self.client.get(url)
        resp_alerts = self.client.get(url_alerts)
        resp_ajax = self.client.get(url_ajax)

        self.assertTrue(resp.status_code, 200)
        self.assertTrue(resp_ajax.status_code, 200)
        self.assertTrue(resp_alerts.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)
        self.assertIn(ltc_coin.ticker.encode(), resp.content)
        self.assertIn(eth_coin.ticker.encode(), resp.content)
        self.assertIn(eur_coin.ticker.encode(), resp.content)


class CoinPricesTest(TestCase):
    """ Tests for trading and models """
    def test_coin_creation(self):
        """ Checks for correct behaviour of coin creation """
        btc_coin = create_coin(ticker="tst", name="test", pk=1)
        self.assertTrue(isinstance(btc_coin, CoinPrices))
        self.assertEqual(btc_coin.__str__(), btc_coin.ticker + ' - ' +
                         str(btc_coin.current_price))

    def test_btc_buy_view(self):
        """ Checks for correct behaviour of btc trading page """
        btc_coin = create_coin(ticker="btc", name="bitcoin", pk=1)
        url = '/dashboard/1/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)
        self.assertIn(str("LSTM").encode(), resp.content)
        self.assertIn(str("Support").encode(), resp.content)
        self.assertIn(str("Chart Analysis").encode(), resp.content)
        self.assertIn(str("Wallet").encode(), resp.content)

    def test_ltc_buy_view(self):
        """ Checks for correct behaviour of ltc trading page """
        btc_coin = create_coin(ticker="ltc", name="litecoin", pk=2)
        url = '/dashboard/2/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)


    def test_eth_buy_view(self):
        """ Checks for correct behaviour of eth trading page """
        btc_coin = create_coin(ticker="eth", name="ethereum", pk=3)
        url = '/dashboard/3/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)

    def test_eur_buy_view(self):
        """ Checks for correct behaviour of eur trading page """
        btc_coin = create_coin(ticker="eur", name="ethereum", pk=4)
        url = '/dashboard/4/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)

    def test_btc_buy_view_FAIL(self):
        """ Checks for correct behaviour of btc trading page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker="btc", name="bitcoin", pk=2)
        url = '/dashboard/1/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(btc_coin.ticker.encode(), resp.content)

    def test_ltc_buy_view_FAIL(self):
        """ Checks for correct behaviour of ltc trading page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker="ltc", name="litecoin", pk=3)
        url = '/dashboard/2/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(btc_coin.ticker.encode(), resp.content)

    def test_eth_buy_view_FAIL(self):
        """ Checks for correct behaviour of ltc trading page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker="eth", name="ethereum", pk=4)
        url = '/dashboard/3/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(btc_coin.ticker.encode(), resp.content)

    def test_eur_buy_view_FAIL(self):
        """ Checks for correct behaviour of ltc trading page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker="eth", name="ethereum", pk=5)
        url = '/dashboard/3/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(btc_coin.ticker.encode(), resp.content)

    def test_forms(self):
        """ testing forms """
        form = BuyForm(prefix='buy')
        self.assertTrue(not form.is_valid())


class ChartAnalysisTest(TestCase):
    """ Tests for chart analysis view"""
    def test_btc_chartAnalysis(self):
        """ Checks for correct behaviour of btc chart analysis page """
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        url = '/chartAnalysis/' + str(btc_coin.ticker)+"/"
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)

    def test_eth_chartAnalysis(self):
        """ Checks for correct behaviour of eth chart analysis page """
        btc_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        url = '/chartAnalysis/' + str(btc_coin.ticker)+"/"
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)

    def test_ltc_chartAnalysis(self):
        """ Checks for correct behaviour of ltc chart analysis page """
        btc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        url = '/chartAnalysis/' + str(btc_coin.ticker)+"/"
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)

    def test_btc_chartAnalysis_FAIL(self):
        """ Checks for correct behaviour of btc chart analysis page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker='BTC', name='bitcoin', pk=2)
        url = '/chartAnalysis/btc/'
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 404)

    def test_eth_chartAnalysis_FAIL(self):
        """ Checks for correct behaviour of eth chart analysis page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker='ETH', name='ethereum', pk=3)
        url = '/chartAnalysis/eth/'
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 404)

    def test_ltc_chartAnalysis_FAIL(self):
        """ Checks for correct behaviour of ltc chart analysis page when
        failure is the desired outcome """
        btc_coin = create_coin(ticker='LTC', name='litecoin', pk=4)
        url = '/chartAnalysis/ltc/'
        resp = self.client.get(url)
        self.assertTrue(resp.status_code, 404)

    def test_chart_ta(self):
        dict = json.loads(get_btc_chart())
        print(dict)
        self.assertTrue("open" in dict[0])


class TestAnalytics(TestCase):
    """ Test for Analytics """
    def test_analytics(self):
        """ ensure analytics page displays
        and contains the correct elements """
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        ltc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        eth_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        eur_coin = create_coin(ticker='eur', name='euro', pk=4)
        url = '/analytics/intraday/'
        resp = self.client.get(url)
        self.assertTrue(resp.status_code, 200)
        self.assertIn(str("trade").encode(), resp.content)
        self.assertIn(btc_coin.ticker.encode(), resp.content)
        self.assertIn(ltc_coin.ticker.encode(), resp.content)
        self.assertIn(eth_coin.ticker.encode(), resp.content)
        self.assertIn(eur_coin.ticker.encode(), resp.content)

    def test_daily_analytics(self):
        """ ensure daily analytics page displays and
        contains the correct elements """
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        ltc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        eth_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        eur_coin = create_coin(ticker='eur', name='euro', pk=4)
        url = '/analytics/daily/'
        url_ajax = '/analytics/api/chart/data/'
        resp_ajax = self.client.get(url_ajax)
        resp = self.client.get(url)

        self.assertTrue(resp.status_code, 200)
        self.assertTrue(resp_ajax.status_code, 200)
        self.assertIn(str("trade").encode(), resp.content)
        self.assertIn(btc_coin.ticker.encode(), resp.content)
        self.assertIn(ltc_coin.ticker.encode(), resp.content)
        self.assertIn(eth_coin.ticker.encode(), resp.content)
        self.assertIn(eur_coin.ticker.encode(), resp.content)

    def test_dynamoDB(self):
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        dynamoTable = dynamodb.Table('trade_stats')
        dynamoTableDaily = dynamodb.Table('daily_trade_stats')
        response = dynamoTable.scan()
        response_daily = dynamoTableDaily.scan()
        self.assertFalse(not response)
        self.assertFalse(not response_daily)

    def test_listCoins(self):
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        ltc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        eth_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        eur_coin = create_coin(ticker='eur', name='euro', pk=4)
        all_coins = CoinPrices.objects.all()
        self.assertFalse(not all_coins)

    def test_listCoins_FAIL(self):
        all_coins = CoinPrices.objects.all()
        self.assertTrue(not all_coins)


class MachineLearningTest(TestCase):
    """ Test Machine learning Module """
    def test_visualisation_page(self):
        """ ensure machine learning page contains the correct
        images and ticker information,
        and loads correctly"""
        btc_coin = create_coin(ticker='btc', name='bitcoin', pk=1)
        ltc_coin = create_coin(ticker='ltc', name='litecoin', pk=3)
        eth_coin = create_coin(ticker='eth', name='ethereum', pk=2)
        eur_coin = create_coin(ticker='eur', name='euro', pk=4)
        url = '/machinelearning/visualisation/'
        resp = self.client.get(url)

        list = get_stats(eur_coin.ticker)

        url_ajax = '/machinelearning/api/chart/data/'
        resp_ajax = self.client.get(url_ajax)

        self.assertTrue(len(list) == 9)
        self.assertTrue(resp.status_code, 200)
        self.assertTrue(resp_ajax.status_code, 200)
        self.assertIn(btc_coin.ticker.encode(), resp.content)
        self.assertIn(ltc_coin.ticker.encode(), resp.content)
        self.assertIn(eth_coin.ticker.encode(), resp.content)
        self.assertIn(eur_coin.ticker.encode(), resp.content)
        self.assertIn(btc_coin.coin_logo.encode(), resp.content)
        self.assertIn(ltc_coin.coin_logo.encode(), resp.content)
        self.assertIn(eth_coin.coin_logo.encode(), resp.content)
        self.assertIn(eur_coin.coin_logo.encode(), resp.content)

    
class SentimentTest(TestCase):
    """ Test Sentiment Module """
    def test_sentiment(self):
        """ ensure sentiment page contains the correct
        info and loads correctly"""
        sentiment = get_tweet_sentiment("Love")
        self.assertTrue(sentiment == "Negative" or sentiment == "Neutral"
                        or sentiment == "Positive"
                        or sentiment == "Very positive"
                        or sentiment == "Extremely positive")

    def test_analyze_tweets(self):
        """ Tests tweets are successfully being analyzed """
        list = analyze_tweets_numerical("blah")
        print(list)
        for i in list:
            self.assertTrue(type(i) == float)


class TradeTest(TestCase):
    """ Test trading modules """
    def test_fx(self):
        r = get_pos()
        self.assertFalse(not r)