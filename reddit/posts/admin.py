from django.contrib import admin

# Register your models here.
from .models import *

class PostAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'posted_by', 'title', 'posted_in', 'expires_on', 'deleted')

class EventAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'posted_by', 'title', 'posted_in', 'time', 'venue', 'expires_on', 'deleted')

class CommentAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'commented_on', 'comment')

	def comment(self, obj):
		return obj.text[:30]

class VoteAdmin(admin.ModelAdmin):
	list_display = ('voted_by', 'voted_on', 'value')

admin.site.register(TextPost, PostAdmin)
admin.site.register(LinkPost, PostAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
