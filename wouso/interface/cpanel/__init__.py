from django.db.models import get_models
from wouso.core.game.models import Game

def get_cpanel_games():
    # TODO: use get_games and some has_cpanel/cpanel_url_module property!!!
    import os
    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'games'))

    wgs = []
    for g in os.listdir(games_dir):
        if os.path.exists(games_dir + '/' + g + '/cpanel_urls.py'):
            wgs.append(g)

    return wgs
