# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-01 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_coinprices_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coinprices',
            name='image',
            field=models.CharField(max_length=1000),
        ),
    ]