from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.interface.apps.lesson.cpanel_views',
    url(r'^$', 'lessons', name='lessons'),
    url(r'^add_lesson/$', 'add_lesson', name='add_lesson'),
    url(r'^manage_categories/$', 'manage_categories', name='manage_categories'),
    url(r'^add_category/$', 'add_category', name='add_category'),
    url(r'^edit_category/(?P<pk>\d+)/$', 'edit_category', name='edit_category'),
    url(r'^delete_category/(?P<pk>\d+)/$', 'delete_category', name='delete_category'),
)
