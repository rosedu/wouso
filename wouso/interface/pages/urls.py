from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.pages.views.news_index', name='news_index_view'),
    url(r'^(?P<item_id>\d+)/$', 'wouso.interface.pages.views.news_item', name='news_item_view'),
)
