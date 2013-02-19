from django.conf.urls.defaults import *
from cpanel_views import *

urlpatterns = patterns('',
    url(r'^$', CpanelHome.as_view(), name='sc_home'),
    url(r'^challenge/(?P<pk>\d+)/$', CpanelChallenge.as_view(), name='sc_challenge'),
)
