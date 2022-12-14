from django.conf.urls import patterns, url

urlpatterns = patterns(
    'wouso.interface.apps.lesson.cpanel_views',
    url(r'^$', 'lessons', name='lessons'),
    url(r'^add_lesson/$', 'add_lesson', name='add_lesson'),
    url(r'^edit_lesson/(?P<id>\d+)/$', 'edit_lesson', name='edit_lesson'),
    url(r'^delete_lesson/(?P<pk>\d+)/$', 'delete_lesson', name='delete_lesson'),
    url(r'^manage_categories/$', 'manage_categories', name='manage_lesson_categories'),
    url(r'^add_category/$', 'add_category', name='add_lesson_category'),
    url(r'^edit_category/(?P<pk>\d+)/$', 'edit_category', name='edit_lesson_category'),
    url(r'^delete_category/(?P<pk>\d+)/$', 'delete_category', name='delete_lesson_category'),
    url(r'^manage_tags/$', 'manage_tags', name='manage_lesson_tags'),
    url(r'^add_tag/$', 'add_tag', name='add_lesson_tag'),
    url(r'^edit_tag/(?P<pk>\d+)/$', 'edit_tag', name='edit_lesson_tag'),
    url(r'^delete_tag/(?P<pk>\d+)/$', 'delete_tag', name='delete_lesson_tag'),
    url(r'^sort_tags/(?P<id>\d+)/$', 'sort_tags', name='sort_lesson_tags'),
    url(r'^sort_lessons/(?P<id>\d+)/$', 'sort_lessons', name='sort_lessons'),
    url(r'^switch_active/(?P<id>\d+)/$', 'lesson_switch_active', name='lesson_switch_active'),
    url(r'^actions/$', 'lesson_actions', name='lesson_actions'),
)
