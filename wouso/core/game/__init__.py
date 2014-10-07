from django.db.models import get_models, get_app
from models import Game

games_list = []

def get_games():
    """ Returns a list of Game classes """
    global games_list
    if not games_list:
        for model in get_models():
            if Game in model.__bases__:
                games_list.append(model)
        # Quiz models won't show in get_models() list for some reason
        # TODO: Fix it
        for model in get_models(get_app('quiz')):
            if Game in model.__bases__:
                games_list.append(model)
    return games_list
