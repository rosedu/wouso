from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.games.quiz.cpanel_views',
    url(r'^$', 'list_quizzes', name='list_quizzes'),
    url(r'^add_quiz/$', 'add_quiz', name='add_quiz'),
    url(r'^edit_quiz/(?P<pk>\d+)/$', 'edit_quiz', name='edit_quiz'),
    url(r'^delete_quiz/(?P<pk>\d+)/$', 'delete_quiz', name='delete_quiz'),
    url(r'^manage_categories/$', 'manage_categories', name='manage_quiz_categories'),
    url(r'^add_category/$', 'add_category', name='add_quiz_category'),
    url(r'^edit_category/(?P<pk>\d+)/$', 'edit_category', name='edit_quiz_category'),
    url(r'^delete_category/(?P<pk>\d+)/$', 'delete_category', name='delete_quiz_category'),
)
