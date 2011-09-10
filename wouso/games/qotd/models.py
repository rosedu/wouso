from datetime import date, datetime, time
from django.db import models
from django.utils.translation import ugettext_noop
from wouso.interface.activity import signals
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core import scoring
from wouso.core.qpool.models import Schedule
from wouso.core.scoring.models import Formula

# Qotd uses questions from qpool

class QotdUser(Player):
    """ Extension of the User object, customized for qotd """
    last_answered = models.DateTimeField(null=True, blank=True, default=None)
    last_answer = models.IntegerField(default=0, blank=True)
    last_answer_correct = models.BooleanField(default=0, blank=True)

    def set_answered(self, choice, correct):
        if not self.has_answered:
            self.last_answer = choice # answer id
            self.last_answer_correct = correct
            self.last_answered = datetime.now()
            self.save()
            # send signal
            if correct:
                signal_msg = ugettext_noop('{user} has given a correct answer to QotD.')
            else:
                signal_msg = ugettext_noop('{user} has given a wrong answer to QotD.')

            signals.addActivity.send(sender=None, user_from=self,
                                     user_to=self,
                                     message=signal_msg,
                                     arguments={'user': self},
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
            today_start = datetime.combine(now, time())
            today_end = datetime.combine(now, time(23, 59, 59))
            return today_start <= self.last_answered <= today_end

class QotdGame(Game):
    """ Each game must extend Game """
    class Meta:
        # The verbose_name is used in fine printing
        verbose_name = "Question of the Day"
        # A Game extending core.game.models.Game should be set as proxy
        proxy = True

    @staticmethod
    def get_for_today():
        """ Return a Question object selected for Today """
        #question = get_questions_with_tag_for_day("qotd", date.today())
        try:
            sched = Schedule.objects.get(day=date.today())
        except Schedule.DoesNotExist:
            return None
        if not sched or not sched.question.active:
            return None
        return sched.question

    @staticmethod
    def answered(user, question, choice):
        correct = False
        for i, a in enumerate(question.answers):
            if a.id == choice:
                if a.correct:
                    correct = True
                break

        user.set_answered(choice, correct) # answer id

        if correct:
            scoring.score(user, QotdGame, 'qotd-ok')

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        qotd_game = kls.get_instance()
        fs.append(Formula(id='qotd-ok', formula='points=3',
            owner=qotd_game.game,
            description='Points earned on a correct answer')
        )
        return fs

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None
