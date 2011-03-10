from wouso.core.game import get_games
from wouso.core.game.models import Game
from wouso.interface import logger, render_response
   
def games(request):
    """ List of games """
    wgs = []
    for model in get_games():
        wgs.append({'link': model._meta.app_label, 
            'name': model._meta.verbose_name}
        )
        
    return render_response('games.html', 
            request,
            {'games': wgs})

