from django.conf.urls import patterns, url 

urlpatterns = patterns('wouso.games.quiz.cpanel_views',
    url(r'^$', 'list_quizzes', name='list_quizzes'),
    url(r'^add_quiz/$', 'add_quiz', name='add_quiz'),
    url(r'^del/(?P<id>\d+)/$', 'delete_quiz', name='delete_quiz'),
)
