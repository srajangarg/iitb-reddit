from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^subscribe$', views.subscribe, name='subscribe'),
url(r'^unsubscribe$', views.unsubscribe, name='unsubscribe'),
url(r'^deleteMod$', views.addModerator, name='addmoderator'),
url(r'^addMod$', views.delModerator, name='deletemoderator'),
url(r'^addsubreddit$', views.addSubreddit, name='addsubreddit'),
url(r'^add$', views.addSubredditForm, name='addsubredditform'),
url(r'^(.*)$', views.index, name='subreddit'),
]