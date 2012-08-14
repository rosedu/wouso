from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.workshop.views',
    url(r'^$', 'index', name='workshop_index_view'),
    url(r'^play/$', 'play', name='workshop_play'),
    url(r'^review/(?P<workshop>\d+)/$', 'review', name='workshop_review'),
)
