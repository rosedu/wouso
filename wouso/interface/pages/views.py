from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import logger
from models import StaticPage

def staticpage(request, slug):
    """ Perform regular search by either first or last name """
    staticpage = StaticPage.objects.get(slug=slug)
    return render_to_response('static_page.html',
                              {'staticpage': staticpage},
                              context_instance=RequestContext(request))
