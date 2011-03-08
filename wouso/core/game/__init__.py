from django.db.models import get_models
from models import Game

def get_games():
    """ Returns a list of Game classes """
    wgs = []
    for model in get_models():
        if Game in model.__bases__:
            wgs.append(model)
    return wgs
