from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wouso.interface.profile.views',
    url(r'^race/(?P<race_id>\d+)/.*$', 'player_race', name='race_view'),
    url(r'^contact/(?P<player>\d+)/$', 'player_contact', name='player_contact'),
)
