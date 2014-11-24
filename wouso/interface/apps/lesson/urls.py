from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.apps.lesson.views',
    url(r'^$', 'index', name='lesson_index_view'),
    url(r'^(?P<id>\d+)/$', 'lesson', name='lesson_view'),
)

urlpatterns += patterns('wouso.games.quiz.views',
    url(r'^(?P<id>\d+)/$', 'quiz', name='quiz_view'),
)
