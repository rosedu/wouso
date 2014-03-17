import logging
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings
from wouso.core.game import get_games
from wouso.core.config.models import Setting
from wouso.core.magic.models import Bazaar
from wouso.interface.apps import get_apps
from wouso.interface.apps.messaging.models import Message
from wouso.interface.chat.models import Chat
from wouso.interface import get_static_pages, detect_mobile, mobile_browser
from wouso.settings import FORCE_SCRIPT_NAME
from . import set_theme

def context(request):
    """ Make all configuration settings available as config_name
    and also define some game context
    """
    settings_dict = {}
    settings_dict['basepath'] = FORCE_SCRIPT_NAME
    for s in Setting.objects.all():
        settings_dict['config_' + s.name.replace('-','_').lower()] = s.get_value()
    # Special config
    if not settings.CHAT_ENABLED:
        settings_dict['config_disable_chat'] = True
        settings_dict['config_disable_private_chat'] = True
    else:
        settings_dict['config_chat_host'] = settings.SOCKETIO_HOST
        settings_dict['config_chat_port'] = settings.SOCKETIO_PORT

    for k, v in settings_dict.iteritems():
        if k.startswith('config_disable'):
            try:
                settings_dict[k] = bool(v)
            except ValueError: pass

    # user defined theme
    if request.user.is_authenticated():
        custom_theme = settings_dict.get('config_theme_user_%d' % request.user.get_profile().id, None)
        if custom_theme:
            settings_dict['config_theme'] = custom_theme
            set_theme(custom_theme)

    # override theme using GET args
    if request.GET.get('theme', None) is not None:
        from wouso.utils import get_themes
        theme = request.GET['theme']
        if theme in get_themes():
            settings_dict['config_theme'] = theme
            set_theme(theme)
    else:
        set_theme(None)

    # shorthand user.get_profile
    settings_dict['player'] = request.user.get_profile() if request.user.is_authenticated() else None

    # do not use minidetector for now
    mobile = detect_mobile(request)
    if mobile:
        settings_dict['base_template'] = 'mobile_base.html'
    else:
        settings_dict['base_template'] = 'site_base.html'
    settings_dict['has_mobile'] = mobile_browser(request)

    if request.GET.get('ajax', False):
        settings_dict['base_template'] = 'interface/ajax_message.html'

    settings_dict['static_pages'] = get_static_pages()
    return settings_dict
