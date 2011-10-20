from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.specialquest.views.index', name='specialquest_index_view'),
    url(r'^task/(?P<task_id>\d+)/$', 'wouso.games.specialquest.views.task', name='specialquest_task_view'),

    url(r'^setup/accept/(?P<group_id>\d+)/$', 'wouso.games.specialquest.views.setup_accept', name='specialquest_accept'),
    url(r'^setup/leave/$', 'wouso.games.specialquest.views.setup_leave', name='specialquest_leave'),
    url(r'^setup/create/$', 'wouso.games.specialquest.views.setup_create', name='specialquest_create'),
    url(r'^setup/invite/(?P<user_id>\d+)/$', 'wouso.games.specialquest.views.setup_invite', name='specialquest_invite'),
    url(r'^group/view/(?P<group_id>\d+)/$', 'wouso.games.specialquest.views.view_group', name='specialquest_group'),
)
