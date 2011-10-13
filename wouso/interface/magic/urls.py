from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.magic.views.bazaar', name='bazaar_home'),
    url(r'^bazaar/buy/(?P<spell>\d+)/$', 'wouso.interface.magic.views.bazaar_buy', name='bazaar_buy'),
    url(r'^bazaar/exchange/$', 'wouso.interface.magic.views.bazaar_exchange', name='bazaar_exchange'),
)