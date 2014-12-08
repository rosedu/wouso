from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from views import TopicView, ForumView, CategoryView


urlpatterns = patterns('',
    url(r'^$', CategoryView.as_view(), name='overview'),
    url(r'^(?P<pk>\d+)/$', ForumView, name='forum'),
    # url(r'^(?P<forum_id>\d+)/create/$', login_required(TopicCreateView.as_view()), name='topic_create'),
    url(r'^topic/(?P<pk>\d+)/$', TopicView.as_view(), name='topic'),
    # url(r'^topic/(?P<pk>\d+)/create/$', login_required(PostCreateView.as_view()), name='post_create'),
)