from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.grandchallenge.cpanel_views',
    url(r'^$', 'grandchalls', name='grandchalls'),
    url(r'^last/$', 'lastchalls', name='lastchalls'),
    url(r'^start/$', 'grandchalls_start', name='grandchalls_start'),
    url(r'^round/$', 'grandchalls_round', name='grandchalls_round'),
    url(r'^results/$', 'grandchalls_results', name='grandchalls_results'),
)