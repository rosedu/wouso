from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.interface.forum.cpanel_views',
    url(r'^$', 'forum', name='forum'),
    url(r'^add_forum/$', 'add_forum', name='add_forum'),
    url(r'^edit_forum/(?P<pk>\d+)/$', 'edit_forum', name='edit_forum'),
    url(r'^delete_forum/(?P<pk>\d+)/$', 'delete_forum', name='delete_forum'),
    url(r'^manage_categories/$', 'manage_forum_categories', name='manage_forum_categories'),
    url(r'^add_category/$', 'add_forum_category', name='add_forum_category'),
    url(r'^edit_category/(?P<pk>\d+)/$', 'edit_forum_category', name='edit_forum_category'),
    url(r'^delete_category/(?P<pk>\d+)/$', 'delete_forum_category', name='delete_forum_category'),
    url(r'^switch_closed/(?P<id>\d+)/$', 'forum_switch_closed', name='forum_switch_closed'),
    url(r'^actions/$', 'forum_actions', name='forum_actions'),
)
