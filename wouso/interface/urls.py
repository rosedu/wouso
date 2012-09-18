from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'wouso.interface.views.homepage', name='homepage'),
    url(r'^hub/$', 'wouso.interface.views.hub', name='hub'),
    url(r'^(?P<page>\d*)/$', 'wouso.interface.views.homepage', name='homepage'),

    # TODO: refactor this into wouso.interface.top.urls and include vvvvv
    url(r'^top/$', 'wouso.interface.top.views.gettop', name='view_top'),
    (r'^top/toptype/(?P<toptype>\d)/sortcrit/(?P<sortcrit>\d)/page/(?P<page>\d+)/$', 'wouso.interface.top.views.gettop'),
    (r'^top/pyramid/$', 'wouso.interface.top.views.pyramid'),
    url(r'^top/classes/$', 'wouso.interface.top.views.topclasses', name='top_classes'),
    # toptype = 0 means overall top
    # toptype = 1 means top for 1 week
    # sortcrit = 0 means sort by points descending
    # sortcrit = 1 means sort by progress descending
    # sortcrit = 2 means sort by last_seen descending

    (r'^user/login/$', 'django.contrib.auth.views.login'),
    (r'^user/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    url(r'^player/(?P<id>\d*)/$', 'wouso.interface.profile.views.user_profile', name='player_profile'),
    url(r'^player/set/$', 'wouso.interface.profile.views.set_profile', name='set_profile'),
    url(r'^player/set/s/$','wouso.interface.profile.views.save_profile', name='player_profile'),
    url(r'^player/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.user_profile', name="player_profile"),
    url(r'^player/(?P<id>\d*)/points-summary/$', 'wouso.interface.profile.views.player_points_history', name='player_points_history'),
    url(r'^player/cast/to-(?P<destination>\d+)/$', 'wouso.interface.apps.magic.views.magic_cast', name='magic_cast'),
    url(r'^player/cast/(?P<destination>\d+)/(?P<spell>\d+)/$', 'wouso.interface.apps.magic.views.magic_cast'),
    url(r'^player/cast/mass_view/$', 'wouso.interface.apps.magic.views.mass_magic_view', name='mass_view'),
    url(r'^player/cast/mass/$','wouso.interface.apps.magic.views.magic_cast_mass', name='mass_cast'),
    url(r'^player2/', include('wouso.interface.profile.urls')),

    url(r'^magic/summary/$', 'wouso.interface.profile.views.magic_summary', name='magic_summary'),
    url(r'^magic/spell/$', 'wouso.interface.profile.views.magic_spell', name='get_spell'),

    url(r'^groups/$', 'wouso.interface.profile.views.groups_index', name='groups_index'),
    url(r'^group/(?P<id>\d*)/.*$', 'wouso.interface.profile.views.player_group', name='player_group'),
    url(r'^group/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.player_group', name='player_group_page'),

    url(r'^search/$', 'wouso.interface.views.search', name='search'),
    (r'^instantsearch/$', 'wouso.interface.views.instantsearch'),
    (r'^searchone/$', 'wouso.interface.views.searchone'),
    url(r'^s/(.+)/$', 'wouso.interface.apps.pages.views.staticpage', name='static_page'),

    # Chat
    (r'^chat/', include('wouso.interface.chat.urls')),

    # Messaging
    (r'^m/', include('wouso.interface.apps.messaging.urls')),

    # News
    (r'^n/', include('wouso.interface.apps.pages.urls')),

    # Statistics
    (r'^stats/', include('wouso.interface.apps.statistics.urls')),

    # Qproposal
    (r'^qproposal/', include('wouso.interface.apps.qproposal.urls')),

    # Bazaar
    url(r'^bazaar/', include('wouso.interface.apps.magic.urls')),

    # Some dynamic shite
    url(r'^ajax/do/(?P<name>.*)/$', 'wouso.interface.views.ajax', name='ajax_do'),
    url(r'^ajax/get/(?P<model>.*)/(?P<id>\d+)/$', 'wouso.interface.views.ajax_get', name='ajax_get'),
    url(r'^ajax/notifications/$', 'wouso.interface.views.ajax_notifications', name='ajax_notifications'),

    # Games
    url(r'^g/', include('wouso.games.urls')),

    # The future
    url(r'^ui/', 'wouso.interface.views.ui', name='ui'),

    # Admin related
    (r'^cpanel/', include('interface.cpanel.urls')),
    (r'^admin/', include(admin.site.urls)),
    #(r'^admin/djangologdb/', include('djangologdb.urls')),

    # Static: not in a real deployment
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)

# API only when we have piston
try:
    import imp
    imp.find_module('piston')
except ImportError:
    urlpatterns += patterns('wouso.interface.views', url(r'^api/', 'no_api'))
else:
    urlpatterns += patterns('', url(r'^api/', include('wouso.interface.api.urls')))

# Specific urls with import logic - soft dependencies
try:
    import imp
    imp.find_module('django_qunit')
except ImportError:
    pass
else:
    urlpatterns += patterns('',
        url(r'^qunit/', include('django_qunit.urls'))
	)
