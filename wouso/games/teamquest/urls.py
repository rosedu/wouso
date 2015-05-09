from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('wouso.games.teamquest.views',
    url(r'^$', 'index', name='teamquest_index_view'),
    url(r'^teamhub/(?P<user_id>\d+)/$', 'teamhub', name='team_hub_view'),
    url(r'^teamhub/create/$', 'setup_create', name='setup_create'),
    url(r'^teamhub/leave/$', 'setup_leave', name='setup_leave'),
    url(r'^teamhub/kick(?P<user_id>\d+)/$', 'setup_kick', name='setup_kick'),
    url(r'^teamhub/invite/$', 'setup_invite', name='setup_invite'),
    url(r'^teamhub/request/$', 'setup_request', name='setup_request'),
    url(r'^teamhub/accept_invitation(?P<invitation_id>\d+)/$', 'setup_accept_invitation', name='setup_accept_invitation'),
    url(r'^teamhub/accept_request(?P<request_id>\d+)/$', 'setup_accept_request', name='setup_accept_request'),
    url(r'^teamhub/decline_invitation(?P<invitation_id>\d+)/$', 'setup_decline_invitation', name='setup_decline_invitation'),
    url(r'^teamhub/decline_request(?P<request_id>\d+)/$', 'setup_decline_request', name='setup_decline_request'),
)
