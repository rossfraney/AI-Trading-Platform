# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-02 21:55
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20180201_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='coinprices',
            name='predictions',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(max_length=9999999), size=None), default=django.utils.timezone.now, size=None),
            preserve_default=False,
        ),
    ]