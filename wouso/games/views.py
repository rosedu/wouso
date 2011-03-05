from django.db.models import get_models
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.game.models import Game
from wouso.interface import logger
   
def games(request):
    """ List of games """
    wgs = []
    for model in get_models():
        if Game in model.__bases__:
            wgs.append({'link': model._meta.app_label, 
                'name': model._meta.verbose_name}
            )
        
    return render_to_response('games.html', 
            {'games': wgs},
            context_instance=RequestContext(request))

