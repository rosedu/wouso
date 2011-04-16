from django.conf.urls.defaults import *
from django.conf import settings
from wouso.games.qotd.feeds import LatestQuestionsFeed

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Project wide pages
    (r'^$', 'wouso.views.homepage'),
    # Question of the day
    (r'^qotd/$', 'wouso.games.qotd.views.index'),
    (r'^qotd/done/$', 'wouso.games.qotd.views.done'),
    (r'^qotd/feed/$', LatestQuestionsFeed()),
    # Challenge
    (r'^challenge/$', 'wouso.games.challenge.views.index'),
    (r'^challenge/(?P<id>\d+)/$', 'wouso.games.challenge.views.challenge'),
    (r'^challenge/launch/(?P<to_id>\d+)/$', 'wouso.games.challenge.views.launch'),
    (r'^challenge/refuse/(?P<id>\d+)/$', 'wouso.games.challenge.views.refuse'),
    (r'^challenge/accept/(?P<id>\d+)/$', 'wouso.games.challenge.views.accept'),
    (r'^challenge/cancel/(?P<id>\d+)/$', 'wouso.games.challenge.views.cancel'),
    # Quest
    (r'^quest/$', 'wouso.games.wquest.views.index'),
    # Activity Wall
    (r'^activity/', include('wouso.extra.activity.urls')),
    
    # Administrator
    (r'^admin/', include(admin.site.urls)),
    
    # Facebook 
    (r'^facebook/', include('facebookconnect.urls')),

    # User management
    (r'^user/login/$', 'django.contrib.auth.views.login', 
        {'template_name': 'user/login.html'}),
    (r'^user/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^user/profile/$', 'wouso.core.profile.views.index'),
    (r'^user/profile/messages/$', 'wouso.core.profile.views.messages'),
    (r'^user/profile/messages/(?P<idmsg>\d+)/$', 'wouso.core.profile.views.message'),
    (r'^user/profile/messages/compose/(?P<idto>\d+)/$', 'wouso.core.profile.views.message_compose'),
    (r'^user/profile/(?P<id>\d+)/$', 'wouso.core.profile.views.user_profile', {}, "user_profile"),
    (r'^user/profile/top/$', 'wouso.core.profile.views.top'),
    (r'^user/profile/search/$', 'wouso.core.profile.views.search'),
    
    # Just for development:
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
