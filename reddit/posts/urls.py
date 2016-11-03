from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^submitpost$', views.submitpost, name='submitpost'),
    url(r'^submit$', views.newpost, name='newpost'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^([0-9]*)$', views.post, name='post'),
]