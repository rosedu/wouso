from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.grandchallenge.cpanel_views',
    url(r'^$', 'grandchalls', name='grandchalls'),
    url(r'^last/$', 'lastchalls', name='lastchalls'),
    url(r'^start/$', 'grandchalls_start', name='grandchalls_start'),
    url(r'^round/$', 'grandchalls_round', name='grandchalls_round'),
    url(r'^round/(?P<round_number>\d+)$', 'grandchalls_round_results', name='grandchalls_round_results'),
    url(r'^round/next/$', 'grandchalls_round_next', name='grandchalls_round_next'),
    url(r'^round/close/$', 'grandchalls_round_close', name='grandchalls_round_close'),
    url(r'^round/reset/$', 'grandchalls_hard_reset', name='grandchalls_hard_reset'),
    url(r'^results/$', 'grandchalls_results', name='grandchalls_results'),
)