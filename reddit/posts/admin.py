from django.contrib import admin

# Register your models here.
from .models import TextPost, LinkPost, Comment, Vote

class PostAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'posted_by', 'title', 'posted_in')

class CommentAdmin(admin.ModelAdmin):
	list_display = ('created_on', 'commented_on', 'text')

class VoteAdmin(admin.ModelAdmin):
	list_display = ('voted_by', 'voted_on', 'value')

admin.site.register(TextPost, PostAdmin)
admin.site.register(LinkPost, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
