from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from wouso.core.ui import register_sidebar_block
from wouso.interface.apps.files.models import FileCategory, File


@login_required
def index(request):
    """ Shows all lessons related to the current user """

    categories = FileCategory.objects.all()

    return render_to_response('files/index.html',
                              {'categories': categories},
                              context_instance=RequestContext(request))


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    if File.disabled():
        return ''

    return render_to_string('files/sidebar.html', {})


register_sidebar_block('files', sidebar_widget)
