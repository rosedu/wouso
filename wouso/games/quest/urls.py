from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'games.quest.views.index'),
)

