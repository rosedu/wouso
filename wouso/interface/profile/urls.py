from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('wouso.interface.profile.views',
    url(r'^race/(?P<race_id>\d+)/.*$', 'player_race', name='race_view'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password_change/$',
        'password_change',
        {'template_name': 'registration/password_change_form.html',
         'post_change_redirect': reverse_lazy('password_change_done')},
        name='password_change'),
    url(r'^password_change_done/$', 'password_change_done', name='password_change_done'),
)
