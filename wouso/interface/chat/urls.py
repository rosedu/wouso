
from django.conf.urls.defaults import *

urlpatterns = patterns('wouso.interface.chat.views',
    (r'^$','index'),
    (r'^chat_m/$','sendmessage'),
    (r'^last/$','online_players'),
    (r'^log/$','log_request'),
    (r'^privateLog/$','private_log')
)

