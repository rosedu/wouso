from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'games.quest.views.index', name='quest_index_view'),
)

