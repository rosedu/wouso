from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'games.grandchallenge.views.index', name='gc_index_view'),
)
