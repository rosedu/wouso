from django.conf.urls import patterns, url


urlpatterns = patterns('wouso.interface.forum.views',
    url(r'^$', 'category', name='overview'),
    url(r'^(?P<pk>\d+)/$', 'forum', name='forum'),
    url(r'^(?P<forum_id>\d+)/create/$', 'topic_create', name='topic_create'),
    url(r'^topic/(?P<pk>\d+)/$', 'topic', name='topic'),
    # url(r'^topic/(?P<pk>\d+)/create/$', login_required(PostCreateView.as_view()), name='post_create'),
)
