# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-22 18:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created_on')),
                ('deleted', models.BooleanField(default=False, verbose_name='deleted')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Upvote'), (-1, 'DownVote')], verbose_name='value')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='posts.Post')),
                ('text', models.TextField(verbose_name='text')),
            ],
            bases=('posts.post',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='posts.Post')),
                ('expires_on', models.DateTimeField(verbose_name='expires_on')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('time', models.DateTimeField(verbose_name='time')),
                ('venue', models.CharField(max_length=50, verbose_name='venue')),
                ('description', models.TextField(verbose_name='description')),
            ],
            bases=('posts.post',),
        ),
        migrations.CreateModel(
            name='LinkPost',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='posts.Post')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('link', models.URLField(verbose_name='link')),
                ('expires_on', models.DateTimeField(verbose_name='expires_on')),
            ],
            bases=('posts.post',),
        ),
        migrations.CreateModel(
            name='TextPost',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='posts.Post')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('text', models.TextField(verbose_name='text')),
                ('expires_on', models.DateTimeField(verbose_name='expires_on')),
            ],
            bases=('posts.post',),
        ),
    ]
