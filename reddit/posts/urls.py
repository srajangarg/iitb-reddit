from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^submitpost$', views.submitpost, name='submitpost'),
    url(r'^submit$', views.newpost, name='newpost'),
    url(r'^(.*)$', views.post, name='post'),
]