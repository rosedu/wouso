from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.games.quiz.views',
    url(r'^$', 'index', name='quiz_index_view'),


)
