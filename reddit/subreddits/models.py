from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_nospace(value):
    if value.find(' ') != -1:
        raise ValidationError(
            _('%(value)s contains space'),
            params={'value': value},
        )

class Subreddit(models.Model):

    created_on = models.DateTimeField('created_on', auto_now_add=True)
    title = models.CharField('title', max_length=20, validators=[validate_nospace], primary_key=True)
    description = models.TextField('description')

    def __unicode__(self):
        return self.title
