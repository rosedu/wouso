from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.games.teamquest.cpanel_views',
    url(r'^$', 'quests', name='teamquest_home'),
    url(r'^groups/$', 'groups', name='teamquest_groups'))
