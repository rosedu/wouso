from random import shuffle
from datetime import datetime

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
    # time when user started quiz
    start = models.DateTimeField(null=True, blank=True)
    # ID of current started quiz
    started_quiz_id = models.IntegerField(default=0)

Player.register_extension('quiz', QuizUser)


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    number_of_questions = models.IntegerField(default=5)
    time_limit = models.IntegerField(default=300)
    questions = models.ManyToManyField(Question)
    owner = models.ForeignKey(Game, null=True, blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField()

    players = models.ManyToManyField(QuizUser)

    @property
    def elapsed(self):
        if self.end < datetime.now():
            return True
        return False

    @property
    def is_active(self):
        acum = datetime.now()
        if self.end < acum:
            return False
        elif self.start > acum:
            return False
        return True

    @classmethod
    def calculate_points(cls, responses):
        """ Response contains a dict with question id and checked answers ids.
        Example:
            {1 : [14,], ...}, - has answered answer with id 14 at the question with id 1
        """
        points = 0
        results = {}
        for r, v in responses.iteritems():
            checked, missed, wrong = 0, 0, 0
            q = Question.objects.get(id=r)
            correct_count = len([a for a in q.answers if a.correct])
            wrong_count = len([a for a in q.answers if not a.correct])
            for a in q.answers.all():
                if a.correct:
                    if a.id in v:
                        checked += 1
                    else:
                        missed += 1
                elif a.id in v:
                    wrong += 1
            if correct_count == 0:
                qpoints = 1 if (len(v) == 0) else 0
            elif wrong_count == 0:
                qpoints = 1 if (len(v) == q.answers.count()) else 0
            else:
                qpoints = checked - wrong
            qpoints = qpoints if qpoints > 0 else 0
            points += qpoints
            results[r] = (checked, correct_count)
        # return {'points': int(100.0 * points), 'results' : results}
        return {'points': points, 'results' : results}

    def add_player(self, player):
        """ Add player to the list of players which have played the quiz
        """
        self.players.add(player)

    def set_start(self, user):
        """ Set quiz start time for user
        """
        user.start = datetime.now()
        user.save()

    def is_started_for_user(self, user):
        """ Check if user has already started quiz
        """
        if user.start is None:
            return False
        return True

    def time_for_user(self, user):
        """ Return seconds left for answering quiz
        """
        now = datetime.now()
        return self.time_limit - (now - user.start).seconds

    def reset(self, user):
        """ Reset quiz start time and ID of current started quiz
        """
        if user.start is not None:
            user.start = None
        if user.started_quiz_id != 0:
            user.started_quiz_id = 0
        user.save()


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
