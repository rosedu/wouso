from django.db import models
from django.contrib.auth.models import User
from core.game.models import Game

# Qotd will use models (question) from qpool
# Please implement wouso.core.qpool

class QotdUser(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='qotd_user')
    
    """ Extension of the User object, customized for qotd """
    has_answered = models.BooleanField(default=False)
    
