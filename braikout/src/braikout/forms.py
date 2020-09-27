from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth import (
    get_user_model,
)

User = get_user_model()


class BuyForm(forms.Form):
    post = forms.FloatField(label='')


class SellForm(forms.Form):
    post = forms.FloatField(label='')


class AlertAboveForm(forms.Form):
    post = forms.FloatField(label='')


class AlertBelowForm(forms.Form):
    post = forms.FloatField(label='')


class AlertSRForm(forms.Form):
    post = forms.FloatField(label='')


class AuthForm(forms.Form):
    post = forms.CharField(label=mark_safe("<p colour='white'> Crypto API </p>"))
    post1 = forms.CharField(label=mark_safe("<p colour='white'> Crypto secret </p>"))
    post2 = forms.CharField(label=mark_safe("<p colour='white'> fx API </p>"))
    post3 = forms.CharField(label=mark_safe("<p colour='white'> fx secret </p>"))
