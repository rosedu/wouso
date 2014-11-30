import os
import re
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
        if not game.disabled():
            game = game.__name__.replace('Game', '')
            if has_cpanel_url(game.lower()):
                url = 'games/' + game.lower()
                # Add space before capital letters (e.g. Special Quest)
                gs[url] = re.sub(r"(\w)([A-Z])", r"\1 \2", game)

    return gs
