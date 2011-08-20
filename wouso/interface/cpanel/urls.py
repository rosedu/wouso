from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.cpanel.views.dashboard'),
)

