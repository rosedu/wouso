import json
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext as _
from wouso.core.game import get_games
from wouso.core.game.models import Game
from wouso.core.user.models import Player
from wouso.interface import logger
from wouso.interface.activity.signals import addActivity

class Activity(models.Model):
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user_from = models.ForeignKey(Player, related_name='user_from')
    user_to = models.ForeignKey(Player, related_name='user_to')
    message_string = models.CharField(max_length=140)
    arguments = models.CharField(max_length=600)
    game = models.ForeignKey(Game)

    @property
    def message(self):
        if self.arguments:
            try:
                arguments = json.loads(self.arguments)
            except Exception as e:
                logger.exception(e)
                arguments = {}
        # emphasize
        for k in arguments.keys():
            arguments[k] = '<strong>%s</strong>' % arguments[k]

        return _(self.message_string).format(**arguments)

    @property
    def game_name(self):
        # FIXME: this is a hack for getting game name.
        # self.game contains objects of type Game, therefore
        # ._meta.verbose_name is not visibile to the parent class
        """ Returns the game name """
        for game in get_games():
            if game.__name__ == self.game.name:
                return game._meta.verbose_name

def addActivity_handler(sender, **kwargs):
    """ Callback function for addActivity signal """
    a = Activity()
    a.user_from = kwargs['user_from']
    a.user_to = kwargs['user_to']
    a.message_string = kwargs['message']
    args = kwargs.get('arguments', {})
    for k in args.keys():
        args[k] = unicode(args[k])
    a.arguments = json.dumps(args)
    a.game = kwargs['game']
    a.save()

addActivity.connect(addActivity_handler)
