from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^(.*)$', views.index, name='subreddit'),
url(r'^subscribe$', views.subscribe, name='subscribe'),
url(r'^add$', views.addSubreddit, name='addsubreddit'),
]