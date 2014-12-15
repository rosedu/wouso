from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^ckeditor/', include('ckeditor.urls')),

    url(r'^$', 'wouso.interface.views.homepage', name='homepage'),
    url(r'^hub/$', 'wouso.interface.views.hub', name='hub'),
    url(r'^(?P<page>\d*)/$', 'wouso.interface.views.homepage', name='homepage'),

    url(r'^activity/all/$', 'wouso.interface.views.all_activity', name='all_activity'),
    url(r'^activity/seen/$', 'wouso.interface.views.seen_24h', name='seen24'),

    (r'^top/', include('wouso.interface.top.urls')),

    (r'^forum/', include('wouso.interface.forum.urls')),

    url(r'^leaderboard/$', 'wouso.interface.views.leaderboard_view', name='leaderboard'),
    url(r'^division/$', 'wouso.interface.views.division_view', name='division'),

    url(r'^user/login/$','wouso.interface.views.login_view', name='login_view'),
    url(r'^user/logout/$','wouso.interface.views.logout_view', name='logout_view'),

    url(r'^player/(?P<id>\d+)/$', 'wouso.interface.profile.views.user_profile', name='player_profile'),
    url(r'^player/set/$', 'wouso.interface.profile.views.set_profile', name='set_profile'),
    url(r'^player/set/s/$','wouso.interface.profile.views.save_profile', name='player_profile'),
    url(r'^player/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.user_profile', name="player_profile"),
    url(r'^player/(?P<id>\d*)/points-summary/$', 'wouso.interface.profile.views.player_points_history', name='player_points_history'),
    url(r'^player/cast/to-(?P<destination>\d+)/$', 'wouso.interface.apps.magic.views.magic_cast', name='magic_cast'),
    url(r'^player/cast/(?P<destination>\d+)/(?P<spell>\d+)/$', 'wouso.interface.apps.magic.views.magic_cast'),

    url(r'^player2/', include('wouso.interface.profile.urls')),

    url(r'^magic/summary/$', 'wouso.interface.profile.views.magic_summary', name='magic_summary'),
    url(r'^magic/spell/$', 'wouso.interface.profile.views.magic_spell', name='get_spell'),
    url(r'^magic/affected_players/$', 'wouso.interface.apps.magic.views.affected_players', name='affected_players'),

    url(r'^groups/$', 'wouso.interface.profile.views.groups_index', name='groups_index'),
    url(r'^group/(?P<id>\d*)/.*$', 'wouso.interface.profile.views.player_group', name='player_group'),
    url(r'^group/(?P<id>\d*)/(?P<page>\d*)/$', 'wouso.interface.profile.views.player_group', name='player_group_page'),

    url(r'^search/$', 'wouso.interface.views.search', name='search'),
    (r'^instantsearch/$', 'wouso.interface.views.instantsearch'),
    (r'^searchone/$', 'wouso.interface.views.searchone'),
    url(r'^s/(.+)/$', 'wouso.interface.apps.pages.views.staticpage', name='static_page'),

    #Lesson
    (r'^lessons/', include('wouso.interface.apps.lesson.urls')),

    #Lesson
    (r'^files/', include('wouso.interface.apps.files.urls')),

    #Report
    url(r'^report/(?P<id>\d*)/$','wouso.core.security.views.report', name='report_player'),

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

    url('', include('social.apps.django_app.urls', namespace='social')),
)

# API only when we have piston
try:
    assert settings.API_ENABLED
    import imp
    imp.find_module('piston')
except (ImportError, AssertionError):
    urlpatterns += patterns('wouso.interface.views', url(r'^api/', 'no_api'))
else:
    urlpatterns += patterns('', url(r'^api/', include('wouso.interface.api.urls')))
