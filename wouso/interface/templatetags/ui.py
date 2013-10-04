from django import template
from wouso.core.ui import get_sidebar
from wouso.core.config.models import Setting
register = template.Library()

@register.simple_tag(takes_context=True)
def render_sidebar(context):
    """
    :return: HTML for the sidebar
    """
    s = get_sidebar()
    order = [k for k in Setting.get('sidebar-order').get_value().split(',') if k]
    if not order:
        order = s.get_blocks()

    content = ''
    for block in order:
        content += s.get_block(block, context)
    return content
