from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()
import wouso.games

urlpatterns = patterns('',
    (r'^$', 'interface.views.homepage'),

    (r'^user/login/$', 'django.contrib.auth.views.login'),
    (r'^user/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^user/profile/$', 'interface.profile.views.profile'),

    # Games
    (r'^g/', include('wouso.games.urls')),

    # Admin related
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/djangologdb/', include('djangologdb.urls')),

    # Static: not in a real deployment
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)

