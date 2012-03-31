__author__ = 'alex'
from wouso.interface.messaging.models import MessageApp
from wouso.interface.magic.models import Bazaar

def get_apps():
    """ Same as wouso.core.game.get_games
    """
    return (MessageApp, Bazaar)