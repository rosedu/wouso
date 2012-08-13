from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.workshop.views',
    url(r'^$', 'index', name='workshop_index_view'),
)
