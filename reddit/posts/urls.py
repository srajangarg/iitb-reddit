from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^submitpost$', views.submitPost, name='submitpost'),
    url(r'^submitcomment$', views.submitComment, name='submitcomment'),
    url(r'^submit$', views.newPost, name='newpost'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^([0-9]*)$', views.post, name='post'),
]