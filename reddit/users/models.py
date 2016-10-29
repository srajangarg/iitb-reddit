from __future__ import unicode_literals

from django.db import models
from subreddits.models import Subreddit
import random

class Redditer(models.Model):

    joined_on = models.DateTimeField('joined_on', auto_now_add=True)
    username = models.CharField('username', max_length=20, primary_key=True)
    password = models.CharField('password', max_length=128)

    def set_password(self, raw_password):
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def __unicode__(self):
        return self.username

class Moderator(models.Model):

    redditer = models.ForeignKey(Redditer)
    subreddit = models.ForeignKey(Subreddit)



