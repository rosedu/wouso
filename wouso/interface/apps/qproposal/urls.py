from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('wouso.interface.apps.qproposal.views',
    url(r'^$', 'propose', name='propose')
)
