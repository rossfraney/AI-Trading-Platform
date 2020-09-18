""" Urls for Dashboard module """
from django.conf.urls import url
from . import views
from .views import ChartData

app_name = 'dashboard'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<coin_id>[0-4]+)/$', views.detail, name='detail'),
    url(r'^(?P<coin_id>[5-6]+)/$', views.forex, name='forex'),
    url(r'^alerts/(?P<coin_id>[0-6]+)/$', views.alerts, name='alerts'),
    url(r'^auth-keys/$', views.auth, name='auth_keys'),
    url(r'^api/chart/data/$', ChartData.as_view()),
]
