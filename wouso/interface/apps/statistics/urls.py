from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('wouso.interface.apps.statistics.views',
    url(r'^$', 'stats', name='stats')
)
