from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.challenge.views',
    url(r'^$', 'index', name='challenge_index_view'),
    url(r'^(?P<id>\d+)/$', 'challenge', name='view_challenge'),
    url(r'^launch/(?P<to_id>\d+)/$', 'launch', name='challenge_launch'),
    url(r'^refuse/(?P<id>\d+)/$', 'refuse', name='challenge_refuse'),
    url(r'^accept/(?P<id>\d+)/$', 'accept', name='challenge_accept'),
    url(r'^cancel/(?P<id>\d+)/$', 'cancel', name='challenge_cancel'),
    url(r'^setplayed/(?P<id>\d+)/$', 'setplayed', name='setplayed'),

    url(r'^use_artifact/$', 'use_one_more', name='challenge_onemore'),

    url(r'^history/(?P<playerid>\d+)/$', 'history', name='chellenge_history'),

    url(r'^playerchallenge/$', 'challenge_player', name='challenge_player'),
    url(r'^randomchallenge/$', 'challenge_random', name='challenge_random'),
    url(r'^stats/$', 'challenge_stats', name='challenge_stats'),
    url(r'^stats/player=(?P<player_id>\d+)/$', 'challenge_stats', name='challenge_stats'),
    url(r'^stats/target=(?P<target_id>\d+)/', 'detailed_challenge_stats', name='detailed_challenge_stats'),
    url(r'^stats/player=(?P<player_id>\d+)/target=(?P<target_id>\d+)/', 'detailed_challenge_stats', name='detailed_challenge_stats'),
)
