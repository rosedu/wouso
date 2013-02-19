from django.conf.urls.defaults import *
from django.conf import settings
from feeds import LatestQuestionsFeed

urlpatterns = patterns('',
    url(r'^$', 'games.qotd.views.index', name='qotd_index_view'),
    url(r'^done/$', 'games.qotd.views.done', name='qotd_done_view'),
    url(r'^feed/$', LatestQuestionsFeed(), name='qotd_feed_view'),
    url(r'^history/$', 'games.qotd.views.history', name='qotd_history_view'),
)
