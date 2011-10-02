from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.specialquest.views.index', name='specialquest_index_view'),
    url(r'^task/(?P<task_id>\d+)/$', 'wouso.games.specialquest.views.task', name='specialquest_task_view'),
)
