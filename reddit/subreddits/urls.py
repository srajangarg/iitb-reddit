from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^subscribe$', views.subscribe, name='subscribe'),
url(r'^unsubscribe$', views.unsubscribe, name='unsubscribe'),
url(r'^add$', views.addSubreddit, name='addsubreddit'),
url(r'^(.*)$', views.index, name='subreddit'),
]