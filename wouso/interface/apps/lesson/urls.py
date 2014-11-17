from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.apps.lesson.views',
    url(r'^$', 'index', name='lesson_index_view'),
)
