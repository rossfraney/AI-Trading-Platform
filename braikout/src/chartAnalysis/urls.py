from django.conf.urls import url

from .views import LtcView, BtcView, EthView
from .views import ChartData


app_name = 'chartAnalysis'
urlpatterns = [
    url(r'^ltc/$', LtcView.as_view(), name='ltc'),
    url(r'^eth/$', EthView.as_view(), name='eth'),
    url(r'^btc/$', BtcView.as_view(), name='btc'),
    url(r'^ltc/api/chart/datacharts/$', ChartData.as_view()),
    url(r'^btc/api/chart/datacharts/$', ChartData.as_view()),
    url(r'^eth/api/chart/datacharts/$', ChartData.as_view()),
]

