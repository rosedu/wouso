from random import shuffle

from django.db import models

from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core.qpool import register_category, get_questions_with_tag_and_category
from wouso.core.qpool.models import Question


class QuizException(Exception):
    pass


class QuizUser(Player):
    """ Extension of the User object, customized for quiz """
    my_question = models.ForeignKey(Question,
                                    related_name="MyQuestion",
                                    null=True)


Player.register_extension('quiz', QuizUser)


class Quiz(models.Model):
    questions = models.ManyToManyField(Question)
    owner = models.ForeignKey(Game, null=True, blank=True)

    LIMIT = 5

    @classmethod
    def create(cls, tag, ignore_questions=False):
        questions = [q for q in get_questions_with_tag_and_category(tag, 'quiz')]
        if (len(questions) < cls.LIMIT) and not ignore_questions:
            raise QuizException('Too few questions')
        shuffle(questions)

        questions_qs = questions[:cls.LIMIT]
        quiz = Quiz.objects.create(owner=None)
        for q in questions_qs:
            quiz.questions.add(q)

        return quiz


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
