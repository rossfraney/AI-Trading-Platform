# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-23 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoinPrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=5)),
                ('current_price', models.FloatField(max_length=10)),
                ('coin_logo', models.CharField(max_length=1000)),
            ],
        ),
    ]