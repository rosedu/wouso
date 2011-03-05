from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'games.qotd.views.index'),
    (r'^done/$', 'games.qotd.views.done')
)
