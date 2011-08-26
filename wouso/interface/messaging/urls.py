from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.messaging.views.home'),
    url(r'^create$', 'wouso.interface.messaging.views.create', name='create'),
    url(r'^create/to=(?P<to>\d*)$', 'wouso.interface.messaging.views.create', name='create_to'),
)
