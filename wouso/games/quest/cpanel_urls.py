from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.quest.cpanel.quest_home', name='quest_home'),
    url(r'^edit/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_edit'),
    url(r'^sort/(?P<id>\d*)/$', 'wouso.games.quest.cpanel.quest_sort', name='quest_sort'),
    url(r'^new/$', 'wouso.games.quest.cpanel.quest_edit', name='quest_new'),
    url(r'^final/create/$', 'wouso.games.quest.cpanel.create_finale', name='quest_create_finale'),
    url(r'^final/results/$', 'wouso.games.quest.cpanel.final_results', name='final_results'),
    url(r'^final/score/$', 'wouso.games.quest.cpanel.final_score', name='final_second_score'),
)
