from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'games.challenge.views.index'),
    (r'^(?P<id>\d+)/$', 'wouso.games.challenge.views.challenge'),
    (r'^launch/(?P<to_id>\d+)/$', 'wouso.games.challenge.views.launch'),
    (r'^refuse/(?P<id>\d+)/$', 'wouso.games.challenge.views.refuse'),
    (r'^accept/(?P<id>\d+)/$', 'wouso.games.challenge.views.accept'),
    (r'^cancel/(?P<id>\d+)/$', 'wouso.games.challenge.views.cancel'),
    (r'^setplayed/(?P<id>\d+)/$', 'wouso.games.challenge.views.setplayed'),
)
