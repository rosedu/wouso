from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'wouso.games.specialquest.views',
    url(r'^$', 'index', name='specialquest_index_view'),
    url(r'^task/(?P<task_id>\d+)/$', 'task', name='specialquest_task_view'),

    url(r'^setup/accept/(?P<group_id>\d+)/$', 'setup_accept', name='specialquest_accept'),
    url(r'^setup/leave/$', 'setup_leave', name='specialquest_leave'),
    url(r'^setup/create/$', 'setup_create', name='specialquest_create'),
    url(r'^setup/invite/(?P<user_id>\d+)/$', 'setup_invite', name='specialquest_invite'),
    url(r'^group/view/(?P<group_id>\d+)/$', 'view_group', name='specialquest_group'),
)
