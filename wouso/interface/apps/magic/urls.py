from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.interface.apps.magic.views',
    url(r'^$', 'bazaar', name='bazaar_home'),
    url(r'^bazaar/buy/(?P<spell>\d+)/$', 'bazaar_buy', name='bazaar_buy'),
    url(r'^bazaar/exchange/$', 'bazaar_exchange', name='bazaar_exchange'),
)