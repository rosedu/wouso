from django.db import models

from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core.qpool import register_category, get_questions_with_category
from wouso.core.qpool.models import Question


class QuizUser(Player):
    """ Extension of the User object, customized for quiz """
    my_question = models.ForeignKey(Question,
                                    related_name="MyQuestion",
                                    null=True)


class Quiz(models.Models):
    questions = models.ManyToManyField(Question)
    owner = models.ForeignKey(Game, null=True, blank=True)

    @classmethod
    def create(cls, ignore_questions=False):
        questions = [q for q in get_questions_with_category('quiz')]
        print questions
        return questions


class QuizGame(Game):
    """ Each game must extend Game"""
    class Meta:
        proxy = True
    QPOOL_CATEGORY = 'quiz'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Quiz"
        self._meta.get_field('short_name').default = ""
        self._meta.get_field('url').default = "quiz_index_view"
        super(QuizGame, self).__init__(*args, **kwargs)

register_category(QuizGame.QPOOL_CATEGORY, QuizGame)
