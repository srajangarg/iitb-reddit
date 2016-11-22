from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^subscribe$', views.subscribe, name='subscribe'),
url(r'^unsubscribe$', views.unsubscribe, name='unsubscribe'),
url(r'^addmod$', views.addModerator, name='addmod'),
url(r'^deletemod$', views.delModerator, name='deletemod'),
url(r'^addsubreddit$', views.addSubreddit, name='addsubreddit'),
url(r'^add$', views.addSubredditForm, name='addsubredditform'),
url(r'^(.*)$', views.index, name='subreddit'),
]