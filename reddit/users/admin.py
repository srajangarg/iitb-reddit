from django.contrib import admin

# Register your models here.
from .models import Redditer, Moderator

class RedditerAdmin(admin.ModelAdmin):
    list_display = ('joined_on', 'username')

class ModeratorAdmin(admin.ModelAdmin):
	list_display = ('redditer', 'subreddit')

admin.site.register(Redditer, RedditerAdmin)
admin.site.register(Moderator, ModeratorAdmin)