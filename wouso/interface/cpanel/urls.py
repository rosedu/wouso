from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.cpanel.views.dashboard', name='dashboard'),
    url(r'^customization/$', 'wouso.interface.cpanel.views.customization', name='customization'),
    url(r'^qpool/$', 'wouso.interface.cpanel.views.qpool_home', name='qpool_home'),
    url(r'^qpool/edit/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.question_edit', name='question_edit'),
    url(r'^qpool/importer/$', 'wouso.interface.cpanel.views.importer', name='importer'),
    url(r'^qpool/importer/send$', 'wouso.interface.cpanel.views.import_from_upload', name='importer_send'),

    # game specific, TODO make them dynamic
    url(r'^quest/$', 'wouso.games.quest.cpanel.quest_home', name='quest_home'),
    url(r'^quest/edit/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_edit'),
    url(r'^quest/new/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_new'),

    url(r'^artifact/set/(?P<id>\d*)/$', 'wouso.interface.cpanel.views.artifactset', name='artifact_set')
)
