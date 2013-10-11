from django import template
from django.conf import settings
from django.template.loader import render_to_string
from wouso.core.config.models import Setting

register = template.Library()

@register.simple_tag
def chat_scripts():
    """
    Dump the chat scris
    :return:
    """
    if settings.CHAT_ENABLED and not Setting.get('disable-Chat').get_value():
        return render_to_string('chat/setup.html', {'chat_host': Setting.get('chat_host').get_value(),
                                                    'chat_port': Setting.get('chat_port').get_value(),
                                                    'basepath': settings.FORCE_SCRIPT_NAME,
        })
    return ''