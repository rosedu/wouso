import os
from django.db.models import get_models
from wouso.core.game.models import Game

def get_cpanel_games():
    # TODO: use get_games and some has_cpanel/cpanel_url_module property!!!
    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'games'))

    wgs = []
    for g in os.listdir(games_dir):
        if os.path.exists(games_dir + '/' + g + '/cpanel_urls.py'):
            wgs.append(g)

    return wgs

def get_control_panel_games():
	games_dir = os.path.abspath(
		os.path.join(os.path.dirname(__file__), '../..', 'games'))

	gs = {}
	for g in os.listdir(games_dir):
		if os.path.exists(games_dir + '/' + g + '/cpanel_urls.py'):
			copy = '/cpanel/games/' + g + '/'
			if 'challenge' in g:
				g = g.replace("challenge", " challenge")
			if 'quest' in g:
				g = g.replace("quest", " quest")
			g = g.title()
			gs[copy] = g
			print copy

	return gs
