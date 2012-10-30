from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.quest.views',
    url(r'^$', 'index', name='quest_index_view'),
    url(r'^history/$', 'history', name='quest_history'),
)

