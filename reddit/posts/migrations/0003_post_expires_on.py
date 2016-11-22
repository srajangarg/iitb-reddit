# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-22 12:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20161121_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='expires_on',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 21, 12, 24, 30, 989217, tzinfo=utc), verbose_name='expires_on'),
        ),
    ]