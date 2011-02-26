from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'interface.views.homepage'),

	(r'^user/login/$', 'django.contrib.auth.views.login'),
    (r'^user/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}), 

    (r'^admin/', include(admin.site.urls)),

	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)

