from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.workshop.views',
    url(r'^$', 'index', name='workshop_index_view'),
    url(r'^play/$', 'play', name='workshop_play'),
    url(r'^review/(?P<workshop>\d+)/$', 'review', name='workshop_review'),
    url(r'^review/change/review=(?P<review>\d+)/$', 'review_change', name='workshop_edit_review'),

    url(r'^results/(?P<workshop>\d+)/$', 'results', name='workshop_results'),
)
