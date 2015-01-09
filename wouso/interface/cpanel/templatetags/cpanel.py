__author__ = 'alex'
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from wouso.interface.cpanel import get_cpanel_games

register = template.Library()


@register.simple_tag
def cpanel_games():
    """ Return a link list with games having a cpanel module """
    # TODO: better approach, put all games in context_processor.
    text = ''
    cpanel_link = reverse('customization_games')

    for g in get_cpanel_games():
        text += u'<li class="%s"><a href="%s%s/">%s</a></li>' % \
                (g, cpanel_link, g, g.capitalize())

    return text


@register.filter(name='add_css')
def add_css(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='get_form_field')
def get_form_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return settings.TEMPLATE_STRING_IF_INVALID
