from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    (r'^m/$', 'wouso.interface.messaging.views.inbox'),
    (r'^m/inbox$', 'wouso.interface.messaging.views.inbox'),
    (r'^m/sentbox$', 'wouso.interface.messaging.views.sentbox'),
    (r'^m/allbox$', 'wouso.interface.messaging.views.allbox'),
    url(r'^m/create$', 'wouso.interface.messaging.views.create', name='create')
)
