__author__ = 'alex'

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication

from handlers import NotificationsHandler
from authentication import SessionAuthentication

sessionauth = SessionAuthentication()
authoauth = OAuthAuthentication(realm='Wouso')
AUTHENTICATORS = [authoauth, sessionauth]
ad = {'authentication': AUTHENTICATORS}

notifications_resource = Resource(handler=NotificationsHandler, **ad)

urlpatterns = patterns('',
    url(r'^notifications/(?P<type>[^/]+)/$', notifications_resource),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)

urlpatterns += patterns('wouso.interface.api.views',
    url(r'^oauth/request_token_ready/$', 'request_token_ready'),
)