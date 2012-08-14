from django.conf.urls.defaults import *
from wouso.interface.cpanel import get_cpanel_games

upat = [
    url(r'^$', 'wouso.interface.cpanel.views.dashboard', name='dashboard'),
    url(r'^customization/$', 'wouso.interface.cpanel.views.customization', name='customization'),
    url(r'^qpool/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/(?P<page>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/tag_questions/$', 'wouso.interface.cpanel.views.tag_questions', name='tag_questions'),
    url(r'^qpool/edit/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_edit', name='question_edit'),
    url(r'^qpool/del/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_del', name='question_del'),
    url(r'^qpool/set_active_categories', 'wouso.interface.cpanel.views.set_active_categories', name='set_active_categories'),
    url(r'^qpool/new/$', 'wouso.interface.cpanel.views.question_edit', name='question_new'),
    url(r'^qpool/switch_active/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_switch', name='switch_active'),
    url(r'^qpool/importer/$', 'wouso.interface.cpanel.views.importer', name='importer'),
    url(r'^qpool/importer/send$', 'wouso.interface.cpanel.views.import_from_upload', name='importer_send'),
    url(r'^qpool/qotd/schedule$', 'wouso.interface.cpanel.views.qotd_schedule', name='qotd_schedule'),
    url(r'^qpool/search/$', 'wouso.interface.cpanel.views.qpool_search', name='qpool_search'),
    url(r'^qpool/(?P<cat>\w*)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/(?P<cat>\w*)/(?P<page>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/(?P<cat>\w*)/tag=(?P<tag>\d+)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/remove_all/(?P<cat>\w+)/$', 'wouso.interface.cpanel.views.remove_all', name='remove_all'),


    url(r'^artifact/$', 'wouso.interface.cpanel.views.artifact_home', name='artifact_home'),
    url(r'^artifact/user_set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.artifactset', name='artifact_set'),
    url(r'^artifact/new/$', 'wouso.interface.cpanel.views.artifact_edit', name='artifact_new'),
    url(r'^artifact/edit/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.artifact_edit', name='artifact_edit'),
    url(r'^artifact/del/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.artifact_del', name='artifact_del'),
    url(r'^artifact/(?P<group>\w*)/$', 'wouso.interface.cpanel.views.artifact_home', name='artifact_home'),

    url(r'^group/set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.groupset', name='group_set'),
    url(r'^staff/toggle/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.stafftoggle', name='staff_toggle'),

    url(r'^players/$', 'wouso.interface.cpanel.views.players', name='all_players'),

    url(r'^add_player/$', 'wouso.interface.cpanel.views.add_player', name='add_player'),
    url(r'^races_groups/$', 'wouso.interface.cpanel.views.races_groups', name='races_groups'),
]

for g in get_cpanel_games():
    upat.append((r'games/{game}/'.format(game=g), include('wouso.games.{game}.cpanel_urls'.format(game=g))))

upat.append(url(r'^games/', 'wouso.interface.cpanel.views.games', name='games_home'))

urlpatterns = patterns('', *upat)
