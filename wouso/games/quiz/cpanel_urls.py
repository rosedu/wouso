from django.conf.urls import patterns, url 

urlpatterns = patterns('wouso.games.quiz.cpanel_views',
    url(r'^$', 'list_quizzes', name='list_quizzes'),
)
