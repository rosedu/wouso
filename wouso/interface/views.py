from django.shortcuts import render_to_response
from django.template import RequestContext

def homepage(request):
    """ First page shown """
    return render_to_response('site_base.html', 
            context_instance=RequestContext(request))
