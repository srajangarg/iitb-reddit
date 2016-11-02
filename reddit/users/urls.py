from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^user/(.*)/$', views.user, name='user'),
    url(r'^submitpost$', views.submitpost, name='submitpost'),
    url(r'^post$', views.post, name='post'),
	# alternative way
    # url(r'^(?P<username>[0-9]+)/$', views.user, name='user'),
    # url(r'^myaccount$', views.myaccount, name='myaccount'),
]