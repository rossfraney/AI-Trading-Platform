""" URLs for analytics namespace"""
from django.conf.urls import url

from analytics.views import ChartData
from . import views

app_name = 'analytics'
urlpatterns = [
    url(r'^intraday/$', views.intraday, name='intraday'),
    url(r'^daily/$', views.daily, name='daily'),
    url(r'api/chart/data/$', ChartData.as_view()),
]

