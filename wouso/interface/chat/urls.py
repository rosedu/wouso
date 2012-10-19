
from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.interface.chat.views',
    url(r'^$', 'index', name='chat_home'),
    url(r'^archive/$','archive', name='archive'),
    (r'^archive_messages', 'archive_messages'),
    (r'^chat_m/$','sendmessage'),
    (r'^last/$','online_players'),
    (r'^log/$','log_request'),
    (r'^privateLog/$','private_log')
)

