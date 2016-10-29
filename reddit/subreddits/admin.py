from django.contrib import admin

# Register your models here.
from .models import Subreddit

class SubredditAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'title')

admin.site.register(Subreddit, SubredditAdmin)