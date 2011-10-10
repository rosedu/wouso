from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$',  'wouso.interface.bazaar.views.bazaar', name='bazaar_home'),
    url(r'^bazaar/buy/(?P<spell>\d+)/$', 'wouso.interface.bazaar.views.bazaar_buy', name='bazaar_buy'),
    url(r'^bazaar/exchange/$', 'wouso.interface.bazaar.views.bazaar_exchange', name='bazaar_exchange'),
)