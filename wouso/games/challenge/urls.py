from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.challenge.views.index', name='challenge_index_view'),
    url(r'^(?P<id>\d+)/$', 'wouso.games.challenge.views.challenge'),
    url(r'^launch/(?P<to_id>\d+)/$', 'wouso.games.challenge.views.launch'),
    url(r'^refuse/(?P<id>\d+)/$', 'wouso.games.challenge.views.refuse'),
    url(r'^accept/(?P<id>\d+)/$', 'wouso.games.challenge.views.accept'),
    url(r'^cancel/(?P<id>\d+)/$', 'wouso.games.challenge.views.cancel'),
    url(r'^setplayed/(?P<id>\d+)/$', 'wouso.games.challenge.views.setplayed'),

    url(r'^use_artifact/$', 'wouso.games.challenge.views.use_one_more'),
)
