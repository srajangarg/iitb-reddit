# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-21 17:12
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redditer',
            name='username',
            field=models.CharField(max_length=30, primary_key=True, serialize=False, validators=[users.models.validate_nospace], verbose_name='username'),
        ),
    ]
