# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-22 14:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_expires_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkpost',
            name='imgurl',
            field=models.URLField(default='static "images/a.png"', verbose_name='imgurl'),
        ),
        migrations.AddField(
            model_name='linkpost',
            name='site',
            field=models.CharField(default='Web', max_length=50, verbose_name='site'),
        ),
        migrations.AddField(
            model_name='textpost',
            name='site',
            field=models.CharField(default='IITB-Reddit', max_length=50, verbose_name='site'),
        ),
        migrations.AlterField(
            model_name='post',
            name='expires_on',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 21, 14, 56, 17, 550255, tzinfo=utc), verbose_name='expires_on'),
        ),
    ]
