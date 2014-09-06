import os
from wouso.core.game import get_games


def has_cpanel_url(game):
    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../..', 'games'))
    return os.path.exists(games_dir + '/' + game + '/cpanel_urls.py')


def get_cpanel_games():
    """
     Returns a dict of games having a cpanel page:
        gs({'games/specialquest':'Special Quest'})
    """
    gs = {}
    for game in get_games():
        game = game.__name__.replace('Game', '')
        if has_cpanel_url(game.lower()):
            url = 'games/' + game.lower()
            if 'challenge' in game:
                game = game.replace("Challenge", " Challenge")
            if 'quest' in game:
                game = game.replace("Quest", " Quest")
            gs[url] = game

    return gs
