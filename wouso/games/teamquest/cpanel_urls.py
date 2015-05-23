from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.games.teamquest.cpanel_views',
    url(r'^$', 'quests', name='teamquest_home'),
    url(r'^groups/$', 'groups', name='teamquest_groups'),
    url(r'^delete_teamquest/(?P<pk>\d+)/$', 'delete_teamquest', name='delete_teamquest'),
    url(r'^new/$', 'add_teamquest', name='teamquest_add'),
#    url(r'^new/questions/$', 'add_teamquestquestions', name='teamquest_questions'))
