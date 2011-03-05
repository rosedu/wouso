from datetime import datetime
from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import User
from wouso.interface import logger

class Activity(models.Model):
    user_from = models.ForeignKey(User)
    user_to = models.ForeignKey(User)
    message = models.CharField(max_length=140)
    game = models.ForeignKey(Game)

    def get_activities(start, end, filter=none, self):
        # TODO: implement Activities filtering
        return Activities.objects.all()[-end:-start].reverse()
