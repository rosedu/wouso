from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.interface.apps.messaging.views',
    url(r'^$', 'home', name='messaging'),
    url(r'^create$', 'create', name='create'),
    url(r'^create/to=(?P<to>\d+)$', 'create', name='create_to'),
    url(r'^create/to=(?P<to>\d+)/reply_to=(?P<reply_to>\d*)$', 'create', name='reply_to'),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name='delete_msg'),

    (r'^view/(?P<mid>\d*)/$', 'message'),

    url(r'^(?P<quiet>q)/(?P<box>\w+)/$', 'home', name='quiet_home'),
    url(r'^(?P<quiet>q)/(?P<box>\w+)/(?P<page>\d*)/$', 'home', name='quiet_home_pag'),
    (r'^(?P<box>\w+)/$', 'home'),
    (r'^(?P<box>\w+)/(?P<page>\d*)/$', 'home'),
)
