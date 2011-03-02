from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import logger

def homepage(request):
    """ First page shown """
    logger.debug('Everything is fine')

    return render_to_response('site_base.html', 
            context_instance=RequestContext(request))
