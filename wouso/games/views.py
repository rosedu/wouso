from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.game import get_games
from wouso.core.game.models import Game
from wouso.interface import logger

def games(request):
    """ List of games """
    wgs = []
    for model in get_games():
        wgs.append({'link': model._meta.app_label,
            'name': model._meta.verbose_name}
        )

    return render_to_response('interface/games.html',
            {'games': wgs},
            context_instance=RequestContext(request))
