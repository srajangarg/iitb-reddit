from django.contrib import admin

# Register your models here.
from .models import TextPost, LinkPost

admin.site.register(TextPost)
admin.site.register(LinkPost)
# admin.site.register(Comment)