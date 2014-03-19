from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.interface.apps.magic.views',
    url(r'^$', 'bazaar', name='bazaar_home'),
    url(r'^bazaar/buy/(?P<spell>\d+)/$', 'bazaar_buy', name='bazaar_buy'),
    url(r'^hof/$', 'artifact_hof', name='artifact_hof'),
    url(r'^hof/(?P<artifact>\d+)/$', 'artifact_hof', name='artifact_hof'),
)