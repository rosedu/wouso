from django.conf.urls import *

urlpatterns = patterns('wouso.games.challenge.cpanel_views',
    url(r'^$', 'list_challenges', name='list_challenges'),
)