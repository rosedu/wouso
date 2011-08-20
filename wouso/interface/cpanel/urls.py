from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.cpanel.views.dashboard'),
    url(r'^customization/$', 'wouso.interface.cpanel.views.customization', name='customization'),
    url(r'^importer/$', 'wouso.interface.cpanel.views.importer', name='importer'),
    url(r'^importer/send$', 'wouso.interface.cpanel.views.import_from_upload', name='importer_send'),
)
