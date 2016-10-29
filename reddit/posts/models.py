from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from users.models import Redditer
from subreddits.models import Subreddit
# Create your models here.

class Post(models.Model):

    created_on = models.DateTimeField('created_on', auto_now_add=True)
    posted_by = models.ForeignKey(Redditer)
    posted_in = models.ForeignKey(Subreddit)

    class Meta:
        abstract = True

class TextPost(Post):

    text = models.TextField('text')

class LinkPost(Post):

    link = models.URLField(max_length=200)
