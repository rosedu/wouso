from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.quest.cpanel.quest_home', name='quest_home'),
    url(r'^edit/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_edit'),
    url(r'^sort/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_sort', name='quest_sort'),
    url(r'^new/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_new'),
)
