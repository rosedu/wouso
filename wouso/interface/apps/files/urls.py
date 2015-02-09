from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.apps.files.views',
    url(r'^$', 'index', name='files_index_view'),
)
