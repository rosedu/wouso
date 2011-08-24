from datetime import datetime
from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import User
from wouso.interface import logger
from wouso.interface.activity.signals import addActivity

class Activity(models.Model):
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user_from = models.ForeignKey(User, related_name='user_from')
    user_to = models.ForeignKey(User, related_name='user_to')
    message = models.CharField(max_length=140)
    game = models.ForeignKey(Game)

    def fromgame(self):
        """ Returns the game name """
        return self.game.name

def addActivity_handler(sender, **kwargs):
    """ Callback function for addActivity signal """
    a = Activity()
    a.user_from = kwargs['user_from']
    a.user_to = kwargs['user_to']
    a.message = kwargs['message']
    a.game = kwargs['game']
    a.save()

addActivity.connect(addActivity_handler)
