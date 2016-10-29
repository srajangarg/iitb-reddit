from django.contrib import admin

# Register your models here.
from .models import Redditer, Moderator

admin.site.register(Redditer)
admin.site.register(Moderator)