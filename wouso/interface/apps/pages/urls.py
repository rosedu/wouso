from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('wouso.interface.apps.pages.views',
    url(r'^$', 'news_index', name='news_index_view'),
    url(r'^(?P<item_id>\d+)/$', 'news_item', name='news_item_view'),
)
