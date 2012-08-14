import os
import hashlib
import logging
import datetime
import subprocess
from django.db import models
from django.utils.translation import ugettext_noop
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core import scoring
from wouso.core.scoring.models import Formula
from wouso.core.qpool.models import Question
from wouso.core.qpool import get_questions_with_tags
from wouso.interface.activity import signals
from wouso import settings

# Quest will use QPool questions tagged 'quest'

class QuestUser(Player):
    current_quest = models.ForeignKey('Quest', null=True, blank=True, default=None)
    current_level = models.IntegerField(default=0, blank=True)
    started_time = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    finished_time = models.DateTimeField(default=None, blank=True, null=True)
    finished = models.BooleanField(default=False, blank=True)

    def is_current(self, quest):
        return (self.current_quest.id == quest.id) if (self.current_quest and quest) else (self.current_quest == quest)

    @property
    def started(self):
        """
        Check if we started the current quest.
        """
        quest = QuestGame.get_current()
        if (not quest) or (not self.current_quest):
            return False
        return self.current_quest.id == quest.id

    @property
    def current_question(self):
        if not self.current_quest:
            return None
        try:
            return self.current_quest.levels[self.current_level]
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
            qr = QuestResult(user=self, quest=self.current_quest, level=self.current_level)
            qr.save()

            if self.current_level < self.current_quest.count:
                return

            # sending the signal
            signal_msg = ugettext_noop("has finished quest {quest}")
            signals.addActivity.send(sender=None, user_from=self,
                                     user_to=self, message=signal_msg,
                                     arguments=dict(quest=self.current_quest.title),
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
        # send activity signal
        signal_msg = ugettext_noop('has started quest {quest}')
        signals.addActivity.send(sender=None,
                                 user_from=self, user_to=self,
                                 message=signal_msg,
                                 arguments=dict(quest=quest.title),
                                 game=QuestGame.get_instance())

class QuestResult(models.Model):
    user = models.ForeignKey('QuestUser')
    quest = models.ForeignKey('Quest')
    level = models.IntegerField(default=0)

class Quest(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    questions = models.ManyToManyField(Question)
    order = models.CharField(max_length=1000, default="", blank=True)

    def get_formula(self, type='quest-ok'):
        """ Allow specific formulas for specific quests.
        Hackish by now, think of a better approach in next version
        TODO
        """
        if type not in ('quest-ok', 'quest-finish-ok', 'finalquest-ok'):
            return None
        try:
            formula = Formula.objects.get(id='%s-%d' % (type, self.id))
        except Formula.DoesNotExist:
            formula = Formula.objects.get(id=type)
        return formula

    def is_final(self):
        final = FinalQuest.objects.filter(id=self.id).count()
        return final > 0

    @property
    def count(self):
        return self.questions.count()

    @property
    def levels(self):
        """ Get questions/levels in specified order """
        if not self.order:
            return self.questions.all()
        else:
            order = [int(i) for i in self.order.split(',')]
            qs = {}
            for q in self.questions.all():
                qs[q.id] = q
            return [qs[i] for i in order]

    @property
    def elapsed(self):
        return datetime.datetime.now() - self.start

    @property
    def remaining(self):
        return self.end - datetime.datetime.now()

    @property
    def is_active(self):
        acum = datetime.datetime.now()
        if self.end < acum:
            return False
        elif self.start > acum:
            return False
        return True

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
            question = self.levels[user.current_level]
        except IndexError:
            logging.error("No such question")
            return False

        if not user.current_level == self.count and \
                answer.lower() == question.answers.all()[0].text.lower():
            # score current progress
            scoring.score(user, QuestGame, self.get_formula('quest-ok'), level=(user.current_level + 1))
            user.current_level += 1
            if user.current_level == self.count:
                user.finish_quest()
                # score finishing
                scoring.score(user, QuestGame, self.get_formula('quest-finish-ok'))
            user.save()
            return True
        return False

    def reorder(self, order):
        self.order = ''
        for i in order:
            self.order += i + ','
        self.order = self.order[:-1]
        self.save()

    def __unicode__(self):
        return "%s - %s %s" % (self.start, self.end, self.title)

class QuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Weekly Quest"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "quest_index_view"
        super(QuestGame, self).__init__(*args, **kwargs)

    @classmethod
    def get_current(cls):
        try:
            return FinalQuest.objects.get(start__lte=datetime.datetime.now(),
                end__gte=datetime.datetime.now())
        except:
            try:
                return Quest.objects.get(start__lte=datetime.datetime.now(),
                                end__gte=datetime.datetime.now())
            except:
                return None

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        quest_game = kls.get_instance()
        fs.append(dict(id='quest-ok', formula='points={level}',
            owner=quest_game.game,
            description='Points earned when finishing a level. Arguments: level.')
        )
        fs.append(dict(id='quest-finish-ok', formula='points=10',
            owner=quest_game.game,
            description='Bonus points earned when finishing the entire quest. No arguments.')
        )
        fs.append(dict(id='finalquest-ok', formula='points={level}+{level_users}',
            owner=quest_game.game,
            description='Bonus points earned when finishing the final quest. Arguments: level, level_users')
        )
        return fs

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

class FinalQuest(Quest):
    def check_answer(self, user, answer):
        self.error = ''
        if user.current_quest.id != self.id:
            user.finish_quest()
            user.set_current(self)
            return False

        try:
            question = self.levels[user.current_level]
        except IndexError:
            logging.error("No such question")

        # Get the checker path
        path = os.path.join(settings.FINAL_QUEST_CHECKER_PATH, 'task-%02d' % (user.current_level + 1), 'check')
        if not os.path.exists(path):
            self.error = 'No checker for level %d' % user.current_level
            return False

        # Run checker path

        args = [path, user.user.username, answer]
        work_dir = os.path.join(settings.FINAL_QUEST_CHECKER_PATH, 'task-%02d' % (user.current_level + 1))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=work_dir)
        retval = p.wait()

        if retval > 1:
            self.error = 'Error running checker for %d' % user.current_level

        if not user.current_level == self.count and \
            (retval == 0):
            scoring.score(user, QuestGame, self.get_formula('quest-ok'), level=(user.current_level + 1))
            user.current_level += 1
            user.save()
            if user.current_level == self.count:
                user.finish_quest()
                scoring.score(user, QuestGame, self.get_formula('quest-finish-ok'))
            return True
        return False

    def give_level_bonus(self):
        for level in xrange(len(self.levels)):
            users = QuestUser.objects.filter(current_level=level)

            for user in users:
                scoring.score(
                        user,
                        QuestGame,
                        self.get_formula('finalquest-ok'),
                        level=level,
                        level_users=users.count()
                )
