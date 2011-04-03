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

def addActivity_handler(sender, **kwargs):
    a = Activity()
    a.user_from = kwargs['user_from']
    a.user_to = kwargs['user_to']
    a.message = kwargs['message']
    a.game = kwargs['game']
    if a.user_from == a.user_to:
        from_name = '%s %s' % (a.user_from.first_name, a.user_from.last_name)
        a.message = a.message % (from_name, a.game._meta.verbose_name)
    else:
        from_name = '%s %s' % (a.user_from.first_name, a.user_from.last_name)
        to_name = '%s %s' % (a.user_to.first_name, a.user_to.last_name)
        a.message = a.message % (from_name, to_name, a.game._meta.verbose_name)
    a.save()

addActivity.connect(addActivity_handler)
