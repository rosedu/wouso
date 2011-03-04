from django.db import models
from core.user.models import UserProfile
from core.game.models import Game

# Qotd will use models (question) from qpool
# Please implement wouso.core.qpool

class QotdUser(UserProfile):
    """ Extension of the User object, customized for qotd """
    has_answered = models.BooleanField(default=False)
    
class QotdGame(Game):
    """ Each game must extend Game """
    class Meta:
        verbose_name = "Question of the Day"
