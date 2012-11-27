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

    url(r'^workshops/$', 'workshops', name='ws_workshops'),
    url(r'^workshops/add/$', 'workshop_add', name='ws_add_workshop'),
    url(r'^workshops/edit/(?P<workshop>\d+)/$', 'workshop_edit', name='ws_edit_workshop'),
    url(r'^workshops/start/(?P<workshop>\d+)/$', 'workshop_start', name='ws_start'),
    url(r'^workshops/stop/(?P<workshop>\d+)/$', 'workshop_stop', name='ws_stop'),
    url(r'^workshops/rev/(?P<workshop>\d+)/$', 'workshop_mark4review', name='ws_mark_for_review'),
    url(r'^workshops/grd/(?P<workshop>\d+)/$', 'workshop_mark4grading', name='ws_mark_for_grading'),
    url(r'^workshops/upd/(?P<workshop>\d+)/$', 'workshop_update_grades', name='ws_update_grades'),
    url(r'^workshops/map/(?P<workshop>\d+)/$', 'workshop_reviewers', name='ws_reviewers_map'),
    url(r'^workshops/ass/(?P<workshop>\d+)/$', 'workshop_assessments', name='ws_view_assessments'),
    url(r'^workshops/ass/(?P<workshop>\d+)/(?P<assessment>\d+)/$', 'workshop_assessments', name='ws_view_assessment'),
    url(r'^workshops/ass/(?P<workshop>\d+)/(?P<assessment>\d+)/change/$', 'workshop_assessment_edit', name='ws_edit_assessment'),
    url(r'^workshops/ass/(?P<workshop>\d+)/(?P<assessment>\d+)/clear/$', 'reset_reviews', name='ws_reset_assessment_reviews'),

    url(r'^grade/assessment/(?P<assessment>\d+)/$', 'workshop_grade_assessment', name='ws_grade_assessment'),

    url(r'^gradebook/(?P<semigroup>\d+)/$', 'gradebook', name='ws_gradebook'),
)
