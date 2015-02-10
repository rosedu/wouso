from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.quiz.views',
    url(r'^$', 'index', name='quiz_index_view'),
    url(r'^cat/(?P<id>\d+)/$', 'category', name='quiz_category_view'),
    url(r'^(?P<id>\d+)/$', 'quiz', name='quiz_view'),
)
