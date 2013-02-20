from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wouso.interface.top.views',
    url(r'^$', 'gettop', name='view_top'),
    url(r'^toptype/(?P<toptype>\d)/sortcrit/(?P<sortcrit>\d)/page/(?P<page>\d+)/$', 'gettop', name='view_top'),
    url(r'^pyramid/$', 'pyramid', name='pyramid'),
    url(r'^challenge/$', 'challenge_top', name='challenge_top'),
    url(r'^challenge/(?P<sortcritno>\d+)/(?P<pageno>\d+)/$', 'challenge_top', name='challenge_top_arg'),
    url(r'^classes/$', 'topclasses', name='top_classes'),
    url(r'^coin/(?P<coin>\w+)/$', 'topcoin', name='top_coin'),
    # toptype = 0 means overall top
    # toptype = 1 means top for 1 week
    # sortcrit = 0 means sort by points descending
    # sortcrit = 1 means sort by progress descending
    # sortcrit = 2 means sort by last_seen descending
)
