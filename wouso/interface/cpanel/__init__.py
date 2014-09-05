import os
from wouso.core.game import get_games


def get_cpanel_games():
    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'games'))

    gs = {}
    for g in os.listdir(games_dir):
        if os.path.exists(games_dir + '/' + g + '/cpanel_urls.py'):
            copy = g
            if 'challenge' in g:
                g = g.replace("challenge", " challenge")
            if 'quest' in g:
                g = g.replace("quest", " quest")
            g = g.title()
            gs[copy] = g

    return gs
