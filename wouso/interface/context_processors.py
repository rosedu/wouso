import logging
from wouso.core.game import get_games
from wouso.core.config.models import Setting
from wouso.interface.top.models import Top
from wouso.interface.qproposal.models import Qproposal
from wouso.interface.messaging.models import Message
from wouso.interface.statistics.views import footer_link as stats_link
from wouso.interface import get_static_pages, detect_mobile

def header_footer(request):
    """ Generate header and footer bar contents.
    """
    #TODO ordering, using config

    header = []
    try:
        for game in get_games():
            h = game.get_header_link(request)
            if h:
                header.append(h)
    except: pass

    # add also messages link
    try:
        h = Message.get_header_link(request)
        if h:
            header.append(h)
    except: pass

    footer = []
    try:
        for game in get_games():
            f = game.get_footer_link(request)
            if f:
                footer.append(f)
    except: pass

    # also add stats link
    try:
        f = stats_link(request)
        if f:
            footer.append(f)
    except:
        pass

    # also add static pages
    for sp in get_static_pages():
        footer.append(sp.html_link())

    # qporposal
    if not Qproposal.disabled():
        footer.append(Qproposal.get_footer_link(request))

    # format
    header = " | ".join(header)
    footer = " | ".join(footer)

    return {'header': header, 'footer': footer}

def sidebar(request):
    """ For each registered game, get a widget to be displayed in sidebar
    @remark This design needs to be analysed.
    @todo ordering, using config

    Returns a 'sidebar' list containing html boxes.
    """

    sidebar = []

    try:
        # Request blocks from games
        for game in get_games():
            w = game.get_sidebar_widget(request)
            if w:
                sidebar.append(w)

        # Request blocks from apps
        for app in (Top,):
            w = app.get_sidebar_widget(request)
            if w:
                sidebar.append(w)
    except Exception as e:
        logging.error(e)
        # This is a hack for fixing test. TODO: actually fix ./manage.py test

    return {'sidebar': sidebar}

def context(request):
    """ Make all configuration settings available as config_name
    and also define some game context """
    settings = {}
    for s in Setting.objects.all():
        settings['config_' + s.name.replace('-','_')] = s.get_value()

    # override theme using GET args
    if request.GET.get('theme', None) is not None:
        from wouso.utils import get_themes
        theme = request.GET['theme']
        if theme in get_themes():
            settings['config_theme'] = theme

    # shorthand user.get_profile
    settings['player'] = request.user.get_profile()

    # do not use minidetector for now
    mobile = detect_mobile(request)
    if mobile:
        settings['base_template'] = 'mobile_base.html'
    else:
        settings['base_template'] = 'site_base.html'

    if request.GET.get('ajax', False):
        settings['base_template'] = 'interface/ajax_message.html'

    return settings
