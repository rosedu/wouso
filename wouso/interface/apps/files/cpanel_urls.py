from django.conf.urls import patterns, url

urlpatterns = patterns('wouso.interface.apps.files.cpanel_views',
    url(r'^$', 'files', name='files'),
    url(r'^add_file/$', 'add_file', name='add_file'),
    url(r'^edit_file/(?P<pk>\d+)/$', 'edit_file', name='edit_file'),
    url(r'^delete_file/(?P<pk>\d+)/$', 'delete_file', name='delete_file'),
    url(r'^manage_categories/$', 'manage_categories', name='manage_file_categories'),
    url(r'^add_category/$', 'add_category', name='add_file_category'),
    url(r'^edit_category/(?P<pk>\d+)/$', 'edit_category', name='edit_file_category'),
    url(r'^delete_category/(?P<pk>\d+)/$', 'delete_category', name='delete_file_category'),
)
