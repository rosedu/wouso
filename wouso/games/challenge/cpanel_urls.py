from django.conf.urls import patterns, url 

urlpatterns = patterns('wouso.games.challenge.cpanel_views',
    url(r'^$', 'list_challenges', name='list_challenges'),
)
