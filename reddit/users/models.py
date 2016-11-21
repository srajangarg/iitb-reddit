from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from subreddits.models import Subreddit
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_nospace(value):
    if value.find(' ') != -1:
        raise ValidationError(
            _('%(value)s contains space'),
            params={'value': value},
        )

class RedditerManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser):

        if not (username or email):
            raise ValueError('Email & username must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password):
        return self._create_user(username, email, password, False, False)

    def create_superuser(self, username, email, password):
        return self._create_user(username, email, password, True, True)

class Redditer(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField('email address', max_length=120, unique=True)
    username = models.CharField('username', max_length=30, primary_key=True, validators=[validate_nospace])

    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    joined_on = models.DateTimeField('joined_on', auto_now_add=True)

    objects = RedditerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.username

class Moderator(models.Model):

    redditer = models.ForeignKey(Redditer)
    subreddit = models.ForeignKey(Subreddit)

class Subscriber(models.Model):

    redditer = models.ForeignKey(Redditer)
    subreddit = models.ForeignKey(Subreddit)
    subscribed_on = models.DateTimeField('created_on', auto_now_add=True)
