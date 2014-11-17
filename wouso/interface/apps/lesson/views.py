from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from wouso.core.ui import register_sidebar_block


@login_required
def index(request):
    """ Shows all lesson related to the current user """
    return render_to_response('lesson/index.html',
                              {},
                              context_instance=RequestContext(request))


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    return render_to_string('lesson/sidebar.html', {})


register_sidebar_block('lesson', sidebar_widget)
