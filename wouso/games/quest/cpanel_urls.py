from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.quest.cpanel',
    url(r'^$', 'quest_home', name='quest_home'),
    url(r'^edit/(?P<id>\d*)/$', 'quest_edit', name='quest_edit'),
    url(r'^sort/(?P<id>\d*)/$', 'quest_sort', name='quest_sort'),
    url(r'^(?P<quest>\d+)/bonus/$', 'quest_bonus', name='quest_bonus'),
    url(r'^new/$', 'quest_edit', name='quest_new'),
    url(r'^final/create/$', 'create_finale', name='quest_create_finale'),
    url(r'^final/results/$', 'final_results', name='final_results'),
    url(r'^final/score/$', 'final_score', name='final_second_score'),
    url(r'^register/(?P<id>\d+)/$', 'register_results', name='register_results'),
)
