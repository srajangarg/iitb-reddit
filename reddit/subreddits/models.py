from __future__ import unicode_literals

from django.db import models

class Subreddit(models.Model):

    created_on = models.DateTimeField('created_on', auto_now_add=True)
    title = models.CharField('title', max_length=20)
