from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'wouso.games.workshop.cpanel.workshop_home', name='workshop_home'),
)
