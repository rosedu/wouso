from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.messaging.views.home'),
    url(r'^create$', 'wouso.interface.messaging.views.create', name='create'),
    url(r'^create/to=(?P<to>\d*)$', 'wouso.interface.messaging.views.create', name='create_to'),
    url(r'^(?P<quiet>q)/(?P<box>\w+)/$', 'wouso.interface.messaging.views.home', name='quiet_home'),
    url(r'^(?P<quiet>q)/(?P<box>\w+)/(?P<page>\d*)/$', 'wouso.interface.messaging.views.home', name='quiet_home_pag'),
    (r'^(?P<box>\w+)/$', 'wouso.interface.messaging.views.home'),
    (r'^(?P<box>\w+)/(?P<page>\d*)/$', 'wouso.interface.messaging.views.home')
)
