from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('wouso.games.teamquest.views',
    url(r'^$', 'index', name='teamquest_index_view'),
)
