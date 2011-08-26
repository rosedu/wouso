from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.messaging.views.inbox'),
    (r'^inbox$', 'wouso.interface.messaging.views.inbox'),
    (r'^sentbox$', 'wouso.interface.messaging.views.sentbox'),
    (r'^allbox$', 'wouso.interface.messaging.views.allbox'),
    url(r'^create$', 'wouso.interface.messaging.views.create', name='create')
)
