from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.workshop.cpanel',
    url(r'^$', 'workshop_home', name='workshop_home'),
    url(r'^edit-spot/(?P<day>\d+)/(?P<hour>\d+)/$', 'edit_spot', name='ws_edit_spot'),
    url(r'^add-semigroup/$', 'add_group', name='ws_add_group'),
    url(r'^edit-semigroup/(?P<semigroup>\d+)$', 'edit_group', name='ws_edit_group'),
    url(r'^kick-off/(?P<player>\d+)/$', 'kick_off', name='ws_kick_off'),

    url(r'^schedule/$', 'schedule', name='ws_schedule'),
    url(r'^schedule/add/$', 'schedule_change', name='ws_schedule_change'),
    url(r'^schedule/edit/(?P<schedule>\d+)/$', 'schedule_change', name='ws_schedule_change'),
)
