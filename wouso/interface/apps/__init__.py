from wouso.core.magic.models import Bazaar

__author__ = 'alex'
from wouso.interface.apps.messaging.models import MessageApp

def get_apps():
    """ Same as wouso.core.game.get_games
    """
    return (MessageApp, Bazaar)