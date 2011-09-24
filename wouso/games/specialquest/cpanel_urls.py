from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.specialquest.cpanel.home', name='specialquest_home'),
    url(r'^edit/(?P<id>\d*)/$', 'wouso.games.specialquest.cpanel.edit', name='specialquest_edit'),
    url(r'^new/$', 'wouso.games.specialquest.cpanel.edit', name='specialquest_new'),
)
