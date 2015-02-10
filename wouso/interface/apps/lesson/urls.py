from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.apps.lesson.views',
    url(r'^$', 'index', name='lesson_index_view'),
    url(r'^cat/(?P<id>\d+)/$', 'category', name='lesson_category_view'),
    url(r'^tag/(?P<id>\d+)/$', 'tag', name='lesson_tag_view'),
    url(r'^(?P<id>\d+)/$', 'lesson', name='lesson_view'),
)

urlpatterns += patterns('wouso.games.quiz.views',
    url(r'^(?P<id>\d+)/$', 'quiz', name='quiz_view'),
)
