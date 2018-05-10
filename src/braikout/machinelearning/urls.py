""" URLs for Machine learning namespace """
from django.conf.urls import url

# looks for a views file in current dir (.) and imports it
from machinelearning.views import ChartData
from . import views

app_name = 'machinelearning'
urlpatterns = [
    url(r'^visualisation/$', views.visualisation, name='visualisation'),
    url(r'^BTC_predictions/$', views.btc_predictions, name='btc_predictions'),
    url(r'^LTC_predictions/$', views.ltc_predictions, name='ltc_predictions'),
    url(r'^ETH_predictions/$', views.eth_predictions, name='eth_predictions'),
    url(r'^EUR_predictions/$', views.eur_predictions, name='eur_predictions'),
    url(r'^GBP_predictions/$', views.gbp_predictions, name='gbp_predictions'),
    url(r'api/chart/data/$', ChartData.as_view()),
]

