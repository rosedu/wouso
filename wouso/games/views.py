from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import logger
   
def games(request):
    """ List of games """
    # TODO: get the list of installed games.
    return render_to_response('games.html', 
            {'games': []},
            context_instance=RequestContext(request))

