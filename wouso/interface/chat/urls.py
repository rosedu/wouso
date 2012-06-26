
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^$','wouso.interface.chat.views.index'),
    (r'^m/$','wouso.interface.chat.views.sendmessage'),
    (r'^last/$','wouso.interface.chat.views.online_players')

)

