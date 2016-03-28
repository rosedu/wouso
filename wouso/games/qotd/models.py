from datetime import date, datetime, time
from django.conf import settings
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_noop
from random import randint, shuffle
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core import scoring, signals
from wouso.core.qpool import register_category
from wouso.core.qpool.models import Schedule, Answer, Question

# Qotd uses questions from qpool


class QotdUser(Player):
    """ Extension of the User object, customized for qotd """
    last_answered = models.DateTimeField(null=True, blank=True, default=None)
    last_answer = models.IntegerField(default=0, blank=True)
    last_answer_correct = models.BooleanField(default=0, blank=True)
    my_question = models.ForeignKey(Question, related_name="Mine", null=True)

    @property
    def has_question(self):
        if self.my_question is None:
            return False
        qdate = self.my_question.schedule
        if not (qdate.day == date.today()):
            return False
        return True

    def set_question(self, question):
        if question and not self.has_question:
            self.my_question = question
            self.save()

    def reset_question(self):
        self.my_question = None
        self.save()

    def set_answered(self, choice, correct):
        if not self.has_answered:
            self.last_answer = choice  # answer id
            self.last_answer_correct = correct
            self.last_answered = datetime.now()
            self.save()
            # send signal
            if correct:
                action_msg = "qotd-correct"
                signal_msg = ugettext_noop('has given \
                                            a correct answer to QotD.')
            else:
                action_msg = "qotd-wrong"
                signal_msg = ugettext_noop('has given a wrong answer to QotD.')

            signals.addActivity.send(sender=None, user_from=self,
                                     user_to=self,
                                     message=signal_msg,
                                     action=action_msg,
                                     game=QotdGame.get_instance())

    def reset_answered(self):
        self.last_answered = None
        self.save()

    @property
    def has_answered(self):
        """ Check if last_answered was today """
        #TODO: test this
        if self.last_answered is None:
            return False
        else:
            now = datetime.now()
            today_start = datetime.combine(now, time(0, 0, 0))
            today_end = datetime.combine(now, time(23, 59, 59))
            return today_start <= self.last_answered <= today_end


class QotdGame(Game):
    """ Each game must extend Game """
    class Meta:
        # A Game extending core.game.models.Game should be set as proxy
        proxy = True

    QPOOL_CATEGORY = 'qotd'

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Question of the Day"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "qotd_index_view"
        super(QotdGame, self).__init__(*args, **kwargs)

    @staticmethod
    def get_for_today():
        """ Return a Question object selected for Today """
        sched = list(Schedule.objects.filter(day=date.today(),
                     question__active=True).all())
        if not sched:
            return None
        shuffle(sched)
        return sched[0].question

    @staticmethod
    def answered(user, question, choice):
        correct = False
        for i, a in enumerate(question.answers):
            if a.id == choice:
                if a.correct:
                    correct = True
                break

        user.set_answered(choice, correct)  # answer id

        if correct:
            now = datetime.now()

            pr = randint(0, 99)

            scoring.score(user, QotdGame, 'qotd-ok', hour=now.hour)
            if pr < settings.QOTD_BONUS_PROB:
                scoring.score(user, QotdGame, 'qotd-ok-bonus', hour=now.hour)

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        qotd_game = kls.get_instance()
        fs.append(dict(name='qotd-ok',
                  expression='points=4 + (1 if {hour} < 12 else -1)',
                  owner=qotd_game.game,
                  description='Points earned on a correct \
                  answer in the morning'))
        fs.append(dict(name="qotd-ok-bonus",
                  expression='points=2',
                  owner=qotd_game.game,
                  description='Points earned in case of bonus')
                  )
        return fs

    @classmethod
    def get_api(kls):
        from api import QotdHandler
        return {r'^qotd/today/$': QotdHandler}

    @classmethod
    def get_modifiers(cls):
        return ['qotd-blind',  # player cannot launch QuestionOfTheDay
                ]

    @classmethod
    def get_history(cls):
        today = datetime.now()
        qs = Schedule.objects.filter(day__lte=today).order_by('-day')[:7]
        return qs

register_category(QotdGame.QPOOL_CATEGORY, QotdGame)
