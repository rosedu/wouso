import logging
from django.template.loader import render_to_string

# Get a specific logger for this module
logger = logging.getLogger('interface')

def render_string(template, data=None):
    """ Provide game context render_to_string, used by widget generators """

    return render_to_string(template,
            dictionary=data)

def get_static_pages():
    """ Return a list of static pages ordered by position, for rendering in footer """
    from wouso.interface.apps.pages.models import StaticPage

    return StaticPage.get_links()

def mobile_browser(request):
    if request.META.has_key("HTTP_USER_AGENT"):
        s = request.META["HTTP_USER_AGENT"].lower()
        for i in ('nokia', 'mobile'):
            if i in s:
                return True
    return False

def detect_mobile(request):
    if request.GET.get('mobile'):
        request.session['mobile'] = request.GET.get('mobile')
    if request.session.get('mobile'):
        return request.session['mobile'] == '1'
    return mobile_browser(request)


_theme = None
def get_theme():
    """
     Return the current theme
    """
    global _theme

    if _theme is None:
        from wouso.core.config.models import Setting
        return Setting.get('theme').value

    return _theme

def set_theme(value):
    """
     Set the current theme, temporary. Give it a None parameter to use the one in db settings.
    """
    global _theme

    _theme = value


def get_custom_theme(player):
    from wouso.core.config.models import Setting
    return Setting.get('theme_user_%d' % player.id).get_value()


def set_custom_theme(player, theme):
    from wouso.utils import get_themes
    from wouso.core.config.models import Setting
    if theme in get_themes():
        Setting.get('theme_user_%d' % player.id).set_value(theme)
        return True
    return False