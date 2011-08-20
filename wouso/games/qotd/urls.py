from django.conf.urls.defaults import *
from django.conf import settings
from feeds import LatestQuestionsFeed

urlpatterns = patterns('',
    (r'^$', 'games.qotd.views.index'),
    (r'^done/$', 'games.qotd.views.done'),
    (r'^feed/$', LatestQuestionsFeed())
)
