from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.cpanel.views.dashboard', name='dashboard'),
    url(r'^customization/$', 'wouso.interface.cpanel.views.customization', name='customization'),
    url(r'^qpool/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/edit/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_edit', name='question_edit'),
    url(r'^qpool/del/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_del', name='question_del'),
    url(r'^qpool/new/$', 'wouso.interface.cpanel.views.question_edit', name='question_new'),
    url(r'^qpool/switch_active/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_switch', name='switch_active'),
    url(r'^qpool/importer/$', 'wouso.interface.cpanel.views.importer', name='importer'),
    url(r'^qpool/importer/send$', 'wouso.interface.cpanel.views.import_from_upload', name='importer_send'),
    url(r'^qpool/qotd/schedule$', 'wouso.interface.cpanel.views.qotd_schedule', name='qotd_schedule'),
    url(r'^qpool/search/$', 'wouso.interface.cpanel.views.qpool_search', name='qpool_search'),
    url(r'^qpool/(?P<cat>\w*)/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),

    # game specific, TODO make them dynamic
    url(r'^quest/$', 'wouso.games.quest.cpanel.quest_home', name='quest_home'),
    url(r'^quest/edit/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_edit'),
    url(r'^quest/sort/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_sort', name='quest_sort'),
    url(r'^quest/new/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_new'),

    url(r'^artifact/set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.artifactset', name='artifact_set'),
    url(r'^group/set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.groupset', name='group_set'),
)
