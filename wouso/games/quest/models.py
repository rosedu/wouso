import logging
import datetime
from django.db import models
from wouso.core.user.models import UserProfile
from wouso.core.game.models import Game
from wouso.core.scoring.models import Formula
from wouso.core.qpool.models import Question
from wouso.core.qpool import get_questions_with_tags
from wouso.interface.activity import signals

# Quest will use QPool questions tagged 'quest'

class QuestUser(UserProfile):
    current_quest = models.ForeignKey('Quest', null=True, blank=True, default=None)
    current_level = models.IntegerField(default=0, blank=True)
    started_time = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    finished_time = models.DateTimeField(default=None, blank=True, null=True)
    finished = models.BooleanField(default=False, blank=True)

    @property
    def current_question(self):
        if not self.current_quest:
            return None
        try:
            return self.current_quest.questions.all()[self.current_level]
        except IndexError:
            return None

    @property
    def time_took(self):
        if not self.finished_time:
            if self.current_quest:
                if self.current_quest.end < datetime.datetime.now():
                    return self.current_quest.end - self.started_time
                else:
                    return datetime.datetime.now() - self.started_time
            else:
                return 0
        else:
            return self.finished_time - self.started_time

    def finish_quest(self):
        if not self.finished:
            # TODO: insert into questresult # Done?
            qr = QuestResult(user=self, quest=self.current_quest, level=self.current_level)
            qr.save()

            # sending the signal
            signal_msg = u"%s has finished quest %s" % \
                          (self, self.current_quest.title)
            signals.addActivity.send(sender=None, user_from=self, \
                                     user_to=self, message=signal_msg, \
                                     game=QuestGame.get_instance())

            # saving finish data
            self.finished = True
            self.finished_time = datetime.datetime.now()
            self.save()

    def set_current(self, quest):
        self.started_time = datetime.datetime.now()
        self.current_quest = quest
        self.current_level = 0
        self.finished = False
        self.finished_time = None
        self.save()

class QuestResult(models.Model):
    user = models.ForeignKey('QuestUser')
    quest = models.ForeignKey('Quest')
    level = models.IntegerField(default=0)

class Quest(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    max_levels = models.IntegerField(default=0)
    questions = models.ManyToManyField(Question)

    @property
    def levels(self):
        return self.questions.count()

    @property
    def elapsed(self):
        return datetime.datetime.now() - self.start

    @property
    def remaining(self):
        return self.end - datetime.datetime.now()

    @property
    def status(self):
        """ Current activity status.
        Note (alexef): I'm not particulary happy with this
        """
        acum = datetime.datetime.now()
        if self.end < acum:
            return "Passed"
        if self.start > acum:
            return "Scheduled"
        return "Active"

    def check_answer(self, user, answer):
        if user.current_quest != self:
            user.finish_quest()
            user.set_current(self)
            return False
        try:
            question = self.questions.all()[user.current_level]
        except IndexError:
            logging.error("No such question")
            return False

        if not user.current_level == self.levels and \
                answer == question.answers.all()[0].text:
            user.current_level += 1
            #scoring.score()
            if user.current_level == self.levels:
                user.finish_quest()
            user.save()
            return True
        return False

    def __unicode__(self):
        return "%s - %s" % (self.start, self.end)

class QuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        verbose_name = "Weekly Quest"
        proxy = True

    @staticmethod
    def get_current():
        try:
            return Quest.objects.get(start__lte=datetime.datetime.now(),
                                end__gte=datetime.datetime.now())
        except Quest.DoesNotExist:
            return None

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        quest_game = kls.get_instance()
        fs.append(Formula(id='quest-ok', formula='points={level}', 
            owner=quest_game.game, 
            description='Points earned when finishing a level. Arguments: level.')
        )
        return fs

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None
