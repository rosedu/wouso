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


def header_footer(request):
    """ Generate header and footer bar contents.
    """
    try:
        reverse('homepage')
    except NoReverseMatch:
        return {}
    #TODO ordering, using config

    def header_generator():
        for game in get_games():
            h = game.get_header_link(request)
            if h:
                yield h, game.get_instance().verbose_name
        for game in [Message, Bazaar, Chat]:
            h = game.get_header_link(request)
            if h:
                yield h, game.__name__

    def footer_generator():
        for game in get_games():
            f = game.get_footer_link(request)
            if f:
                yield f
        for s in get_static_pages():
            yield s
        for a in get_apps():
            f = a.get_footer_link(request)
            if f:
                yield f

    return {'header': header_generator, 'heads': header_generator, 'footer': footer_generator}


def sidebar(request):
    """ For each registered game, get a widget to be displayed in sidebar
    @remark This design needs to be analysed.
    @todo ordering, using config

    Returns a 'sidebar' list containing html boxes.
    """
    def sidebar_generator():
        for game in get_games() + list(get_apps()):
            try:
                w = game.get_sidebar_widget(request)
            except Exception as e:
                logging.exception(e)
                w = None
            if w:
                yield w

    return {'sidebar': sidebar_generator}


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
        set_theme(settings_dict['config_theme'])

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

    return settings_dict
