from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wouso.games.specialquest.cpanel',
    url(r'^$', 'home', name='specialquest_home'),
    url(r'^groups/$', 'groups', name='specialquest_cpanel_groups'),
    url(r'^groups/edit/(?P<pk>\d+)/$', 'group_edit', name='specialquest_group_edit'),

    url(r'^groups/(?P<group>\d+)/toggle/$', 'group_active_toggle', name='specialquest_cpanel_group_toggle'),
    url(r'^groups/(?P<group>\d+)/edit/(?P<player>\d+)/$', 'group_drop_player', name='specialquest_cpanel_drop'),
    url(r'^groups/(?P<group>\d+)/destroy/$', 'group_delete', name='specialquest_cpanel_group_delete'),

    url(r'^edit/(?P<id>\d*)/$', 'edit', name='specialquest_edit'),
    url(r'^new/$', 'edit', name='specialquest_new'),
    url(r'^delete/{0,1}$', 'delete', name='specialquest_delete_none'),
    url(r'^delete/(?P<id>\d*)/$', 'delete', name='specialquest_delete'),

    url(r'^player/(?P<player_id>\d+)/$', 'manage_player', name='specialquest_manage'),
    url(r'^player/set/(?P<player_id>\d+)/(?P<task_id>\d+)/$', 'manage_player_set', name='specialquest_manage_set'),
    url(r'^player/unset/(?P<player_id>\d+)/(?P<task_id>\d+)/$', 'manage_player_unset', name='specialquest_manage_unset'),
)
