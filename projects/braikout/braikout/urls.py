"""braikout URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from braikout.views import login_view, logout_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^machinelearning/', include('machinelearning.urls')),
    url(r'^chartAnalysis/', include('chartAnalysis.urls')),
    url(r'^analytics/', include('analytics.urls')),
    url(r'^$', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
]
