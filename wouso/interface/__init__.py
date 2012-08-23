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
    return StaticPage.objects.filter(hidden=False).order_by('position')

def detect_mobile(request):
    if request.META.has_key("HTTP_USER_AGENT"):
        s = request.META["HTTP_USER_AGENT"].lower()
        for i in ('nokia', 'mobile'):
            if i in s:
                return True
    if request.GET.get('mobile') or request.session.get('mobile'):
        if request.GET.get('mobile'):
            request.session['mobile'] = (request.GET.get('mobile') == '1')
        return request.session.get('mobile')
    return False
