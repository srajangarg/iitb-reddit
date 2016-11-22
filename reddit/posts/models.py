from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from datetime import timedelta
from django.utils import timezone
from users.models import Redditer
from subreddits.models import Subreddit
# Create your models here.

class Post(models.Model):

    created_on = models.DateTimeField('created_on', auto_now_add=True)
    posted_by = models.ForeignKey(Redditer)
    expires_on = models.DateTimeField('expires_on')
    deleted = models.BooleanField('deleted', default=False)

    def __unicode__(self):
        try:
            return self.textpost.__unicode__()
        except:
            try:
                return self.linkpost.__unicode__()
            except:
                return self.comment.__unicode__()

class TextPost(Post):

    posted_in = models.ForeignKey(Subreddit)
    title = models.CharField('title', max_length=200)
    text = models.TextField('text')

    def __unicode__(self):
        return self.title

class LinkPost(Post):

    posted_in = models.ForeignKey(Subreddit)
    title = models.CharField('title', max_length=200)
    link = models.URLField('link', max_length=200)

    def __unicode__(self):
        return self.title

class Comment(Post):

    text = models.TextField('text')
    commented_on = models.ForeignKey(Post, related_name='comment_post')

    def __unicode__(self):
        return self.text[:30]

class Event(Post):

    posted_in = models.ForeignKey(Subreddit)
    title = models.CharField('title', max_length=200)
    time = models.DateTimeField('time')
    venue = models.CharField('venue', max_length=50)
    description = models.TextField('description')

    def __unicode__(self):
        return self.title


class Vote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'DownVote'),
    )
    value = models.SmallIntegerField('value', choices=VOTE_CHOICES)
    voted_by = models.ForeignKey(Redditer)
    voted_on = models.ForeignKey(Post)
