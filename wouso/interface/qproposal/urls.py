from django.conf.urls.defaults import *
#from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.qproposal.views.propose')
)
