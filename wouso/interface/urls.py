from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()
import wouso.games

urlpatterns = patterns('',
    (r'^$', 'wouso.interface.views.homepage'),
    (r'^(?P<page>\d*)/$', 'wouso.interface.views.homepage'),
    # TODO: refactor this into wouso.interface.top.urls and include vvvvv
    (r'^top/$', 'wouso.interface.top.views.gettop'),
    (r'^top/toptype/(?P<toptype>\d)/sortcrit/(?P<sortcrit>\d)/page/(?P<page>\d+)/$', 'wouso.interface.top.views.gettop'),
    # toptype = 0 means overall top
    # toptype = 1 means top for 1 week
    # sortcrit = 0 means sort by points descending
    # sortcrit = 1 means sort by progress descending
    # sortcrit = 2 means sort by last_seen descending

    (r'^user/login/$', 'django.contrib.auth.views.login'),
    (r'^user/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    url(r'^player/(?P<id>\d*)/$', 'wouso.interface.profile.views.user_profile', name='player_profile'),
    (r'^player/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.user_profile'),
    url(r'^player/(?P<id>\d*)/points-summary/$', 'wouso.interface.profile.views.player_points_history', name='player_points_history'),
    url(r'^player/cast/to-(?P<destination>\d+)/$', 'wouso.interface.profile.views.magic_cast', name='magic_cast'),
    (r'^player/cast/(?P<destination>\d+)/(?P<spell>\d+)/$', 'wouso.interface.profile.views.magic_cast'),

    url(r'^magic/summary/$', 'wouso.interface.profile.views.magic_summary', name='magic_summary'),
    url(r'^magic/spell/$', 'wouso.interface.profile.views.magic_spell', name='get_spell'),

    (r'^groups/$', 'wouso.interface.profile.views.groups_index'),
    (r'^group/(?P<id>\d*)/$', 'wouso.interface.profile.views.player_group'),
    (r'^group/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.player_group'),

    (r'^search/$', 'wouso.interface.views.search'),
    (r'^instantsearch/$', 'wouso.interface.views.instantsearch'),
    (r'^searchone/$', 'wouso.interface.views.searchone'),
    url(r'^s/(.+)/$', 'wouso.interface.pages.views.staticpage', name='static_page'),

    # Chat
    (r'^chat/', include('wouso.interface.chat.urls')),

    # Messaging
    (r'^m/', include('wouso.interface.messaging.urls')),

    # Statistics
    (r'^stats/', include('wouso.interface.statistics.urls')),

    # Qproposal
    (r'^qproposal/', include('wouso.interface.qproposal.urls')),

    # Market
    url(r'^market/$', 'wouso.interface.views.market', name='market_home'),
    url(r'^market/buy/(?P<spell>\d+)/$', 'wouso.interface.views.market_buy', name='market_buy'),
    url(r'^market/exchange/$', 'wouso.interface.views.market_exchange', name='market_exchange'),

    # Games
    (r'^g/', include('wouso.games.urls')),

    # Admin related
    (r'^cpanel/', include('interface.cpanel.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/djangologdb/', include('djangologdb.urls')),

    # Static: not in a real deployment
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
