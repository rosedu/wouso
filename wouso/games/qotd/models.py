from datetime import date, datetime, time
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_noop
from random import shuffle
from wouso.interface.activity import signals
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core import scoring
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
        if not self.has_question:
            self.my_question = question
            self.save()

    def reset_question(self):
        self.my_question = None
        self.save()

    def set_answered(self, choice, correct):
        if not self.has_answered:
            self.last_answer = choice # answer id
            self.last_answer_correct = correct
            self.last_answered = datetime.now()
            self.save()
            # send signal
            if correct:
                action_msg = "qotd-correct"
                signal_msg = ugettext_noop('has given a correct answer to QotD.')
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

        user.set_answered(choice, correct) # answer id

        if correct:
            now = datetime.now()
            scoring.score(user, QotdGame, 'qotd-ok', hour=now.hour)

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        qotd_game = kls.get_instance()
        fs.append(dict(id='qotd-ok',
            formula='points=4 + (1 if {hour} < 12 else -1)',
            owner=qotd_game.game,
            description='Points earned on a correct answer in the morning')
        )
        return fs

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

    @classmethod
    def get_api(kls):
        from piston.handler import BaseHandler
        class QotdHandler(BaseHandler):
            methods_allowed = ('GET', 'POST')
            def read(self, request):
                question = kls.get_for_today()
                try:
                    qotduser = request.user.get_profile().get_extension(QotdUser)
                except models.Model.DoesNotExist:
                    raise Http404()
                if question:
                    return {'text': question.text, 'answers': dict([(a.id, a.text) for a in question.answers]),
                            'had_answered': qotduser.has_answered}
                return {}

            def create(self, request):
                question = kls.get_for_today()
                try:
                    qotduser = request.user.get_profile().get_extension(QotdUser)
                except models.Model.DoesNotExist:
                    raise Http404()
                if not question:
                    return {'success': False, 'error': 'No question for today'}
                if qotduser.has_answered:
                    return {'success': False, 'error': 'User already answered'}
                attrs = self.flatten_dict(request.data)
                if 'answer' not in attrs.keys():
                    return {'success': False, 'error': 'Answer not provided'}
                try:
                    answer_id = int(attrs['answer'])
                    answer = Answer.objects.get(pk=answer_id)
                except ValueError, Answer.DoesNotExist:
                    return {'success': False, 'error': 'Invalid answer'}
                else:
                    qotduser.set_answered(answer.id, answer.correct)
                    return {'success': True, 'correct': answer.correct, 'has_answered': qotduser.has_answered}

        return {r'^qotd/today/$': QotdHandler}

    def get_modifiers(self):
        return ['qotd-blind', #player cannot launch QuestionOfTheDay
                ]
