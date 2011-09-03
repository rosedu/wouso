from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.statistics.views.stats', name='stats')
)
