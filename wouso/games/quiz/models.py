from django.db import models

from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core.qpool.models import Question


class QuizUser(Player):
    """ Extension of the User object, customized for quiz """
    my_question = models.ForeignKey(Question, related_name="MyQuestion", null=True)


class QuizGame(Game):
    """ Each game must extend Game"""
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Quiz"
        self._meta.get_field('short_name').default = ""
        self._meta.get_field('url').default = "quiz_index_view"
        super(QuizGame, self).__init__(*args, **kwargs)
