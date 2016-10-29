from django.contrib import admin

# Register your models here.
from .models import Subreddit

admin.site.register(Subreddit)