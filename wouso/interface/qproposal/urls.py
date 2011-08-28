from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.qproposal.views.propose', name='propose')
)
