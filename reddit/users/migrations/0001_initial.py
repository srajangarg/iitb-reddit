# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subreddits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Moderator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Redditer',
            fields=[
                ('joined_on', models.DateTimeField(auto_now_add=True, verbose_name='joined_on')),
                ('username', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='username')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
            ],
        ),
        migrations.AddField(
            model_name='moderator',
            name='redditer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Redditer'),
        ),
        migrations.AddField(
            model_name='moderator',
            name='subreddit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subreddits.Subreddit'),
        ),
    ]