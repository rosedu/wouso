from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.specialquest.cpanel.home', name='specialquest_home'),
    url(r'^groups/$', 'wouso.games.specialquest.cpanel.groups', name='specialquest_cpanel_groups'),
    url(r'^edit/(?P<id>\d*)/$', 'wouso.games.specialquest.cpanel.edit', name='specialquest_edit'),
    url(r'^new/$', 'wouso.games.specialquest.cpanel.edit', name='specialquest_new'),
    url(r'^delete/{0,1}$', 'wouso.games.specialquest.cpanel.delete', name='specialquest_delete_none'),
    url(r'^delete/(?P<id>\d*)/$', 'wouso.games.specialquest.cpanel.delete', name='specialquest_delete'),

    url(r'^player/(?P<player_id>\d+)/$', 'wouso.games.specialquest.cpanel.manage_player', name='specialquest_manage'),
    url(r'^player/set/(?P<player_id>\d+)/(?P<task_id>\d+)/$', 'wouso.games.specialquest.cpanel.manage_player_set', name='specialquest_manage_set'),
    url(r'^player/unset/(?P<player_id>\d+)/(?P<task_id>\d+)/$', 'wouso.games.specialquest.cpanel.manage_player_unset', name='specialquest_manage_unset'),
)
