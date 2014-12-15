from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.forum.views',
    url(r'^$', 'category', name='forums_overview'),
    url(r'^(?P<pk>\d+)/$', 'forum', name='forum'),
    url(r'^(?P<forum_id>\d+)/create/$', 'topic_create', name='topic_create'),
    url(r'^topic/(?P<pk>\d+)/$', 'topic', name='topic'),
    url(r'^topic/(?P<pk>\d+)/(?P<post_id>\d+)/create/$', 'post_create', name='post_create'),
)
