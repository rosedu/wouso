# Quest will use QPool questions tagged 'quest'
import os
import logging
import datetime
import subprocess
from django.db import models
from django.utils.translation import ugettext_noop
from django.conf import settings
from django.db.models import Sum
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core import scoring, signals
from wouso.core.scoring import History
from wouso.core.scoring.models import Formula
from wouso.core.qpool.models import Question


(TYPE_CLASSIC,
 TYPE_CHECKER,
 TYPE_EXTERNAL) = range(3)


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
        if (not quest) or (not self.current_quest_id):
            return False
        return self.current_quest_id == quest.id

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

    def pass_level(self, quest):
        """
        Pass current level. Increment current level and score.
        """
        if self.current_quest.id != quest.id:
            return None
        scoring.score(self, QuestGame, quest.get_formula('quest-ok'), level=(self.current_level + 1), external_id=quest.id)
        self.current_level += 1
        if self.current_level == quest.count:
            self.finish_quest()
            scoring.score(self, QuestGame, quest.get_formula('quest-finish-ok'), external_id=quest.id)
        self.save()
        self.user.get_profile().save()
        return self.current_level

    def finish_quest(self):
        if not self.finished:
            if self.current_level < self.current_quest.count:
                return

            qr = QuestResult(user=self, quest=self.current_quest, level=self.current_level)
            qr.save()

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

    def register_quest_result(self):
        """
        Create a QuestResult entry for the QuestUser's current quest
        """
        if not self.finished:
            qr, created = QuestResult.objects.get_or_create(user=self,
                          quest=self.current_quest, level=self.current_level)

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
    QUEST_TYPES = (
        (TYPE_CLASSIC, 'In site text answers'),
        (TYPE_CHECKER, 'In site answers, verified by checker'),
        (TYPE_EXTERNAL, 'External levels and answers'),
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    questions = models.ManyToManyField(Question)
    order = models.CharField(max_length=1000, default="", blank=True)
    type = models.IntegerField(default=TYPE_CLASSIC, choices=QUEST_TYPES)
    registered = models.BooleanField(default=False)

    def get_formula(self, type='quest-ok'):
        """ Allow specific formulas for specific quests.
        Hackish by now, think of a better approach in next version
        TODO
        """
        if type not in ('quest-ok', 'quest-finish-ok', 'finalquest-ok', 'quest-finish-bonus'):
            return None

        # TODO: use Formula.get here
        try:
            formula = Formula.objects.get(name='%s-%d' % (type, self.id))
        except Formula.DoesNotExist:
            formula = Formula.objects.get(name=type)
        return formula

    def is_final(self):
        final = FinalQuest.objects.filter(id=self.id).count()
        return final > 0

    def is_answerable(self):
        return self.type == TYPE_CLASSIC or self.type == TYPE_CHECKER

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
        if user.current_quest.id != self.id:
            user.register_quest_result()
            user.set_current(self)
            return False
        try:
            question = self.levels[user.current_level]
        except IndexError:
            logging.error("No such question")
            return False

        if not user.current_level == self.count:
            if self.answer_correct(user.current_level, question, answer, user):
                user.pass_level(self)
                return True
        return False

    def answer_correct(self, level, question, answer, user):
        """
        Check if an answer is correct for a question and level.
        """
        if self.type == TYPE_EXTERNAL:
            return False
        elif self.type == TYPE_CHECKER:
            path = os.path.join(settings.FINAL_QUEST_CHECKER_PATH, 'task-%02d' % (level + 0), 'check')
            if not os.path.exists(path):
                self.error = 'No checker for level %d' % level
                return False
            p = subprocess.Popen([path, user.user.username, answer], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(path))
            retval = p.wait()
            if retval > 1:
                self.error = 'Error running checker for %d' % level
                return False
            return retval == 0
        elif self.type == TYPE_CLASSIC:
            answers = [a.__unicode__().lower() for a in question.answers]
            return answer.strip().lower() in answers
        return False

    def reorder(self, order):
        self.order = ''
        for i in order:
            self.order += i + ','
        self.order = self.order[:-1]
        self.save()

    def players_count(self):
        """
        Number of players who attempted the quest
        """
        # exclude players not belonging to a 'can play' race
        return self.questresult_set.exclude(user__race__can_play=False).values('user').distinct().count()

    def players_completed(self):
        """
        Number of players who finished the quest
        """
        return self.questresult_set.filter(level=self.count).exclude(user__race__can_play=False).count()

    def top_results(self):
        """
         Return the first 10 players who finished this quest
        """
        top_results = self.questresult_set.exclude(user__race__can_play=False).order_by('id')
        top_results = [entry for entry in top_results if entry.level == self.count][:10]
        return top_results

    def give_bonus(self):
        for i, r in enumerate(self.top_results()):
            player = r.user.get_extension(Player)
            scoring.score(player, QuestGame, 'quest-finish-bonus', position=i + 1, external_id=self.id)

    def register(self):
        """
        Register the result of all the users who attempted this quest
        """
        if not self.is_active:
            for user in self.questuser_set.all():
                user.register_quest_result()
            self.registered = True
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
            quest =  FinalQuest.objects.get(start__lte=datetime.datetime.now(),
                end__gte=datetime.datetime.now())
        except:
            try:
                quest = Quest.objects.get(start__lte=datetime.datetime.now(),
                                end__gte=datetime.datetime.now())
            except:
                quest = None
        return quest

    @classmethod
    def get_staff_and_permissions(cls):
        return [{'name': 'Quest Staff', 'permissions': ['change_quest']}]

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        quest_game = kls.get_instance()
        fs.append(dict(name='quest-ok', expression='points={level}',
            owner=quest_game.game,
            description='Points earned when finishing a level. Arguments: level.')
        )
        fs.append(dict(name='quest-finish-ok', expression='points=10',
            owner=quest_game.game,
            description='Bonus points earned when finishing the entire quest. No arguments.')
        )
        fs.append(dict(name='quest-finish-bonus', expression='points=fib(12 - {position})',
            owner=quest_game.game,
            description='Bonus points earned when finishing a quest. Given to first 10, argument: position.')
        )
        fs.append(dict(name='finalquest-ok', expression='points={level}+{level_users}',
            owner=quest_game.game,
            description='Bonus points earned when finishing the final quest. Arguments: level, level_users')
        )
        return fs

    @classmethod
    def get_api(kls):
        from api import QuestAdminHandler, QuestAdminUserHandler
        return {r'^quest/admin/$': QuestAdminHandler,
                r'^quest/admin/quest=(?P<quest_id>\d+)/username=(?P<username>[^/]+)/$': QuestAdminUserHandler
        }

    @classmethod
    def final_exists(cls):
        return FinalQuest.objects.all().count() != 0

    @classmethod
    def get_final(cls):
        try:
            return FinalQuest.objects.all()[0]
        except IndexError:
            return None

class FinalQuest(Quest):
    def give_level_bonus(self):
        final = QuestGame.get_final()
        if not final:
            return

        for level in xrange(len(self.levels) + 1):
            if level == 0:
                continue
            users = QuestUser.objects.filter(current_quest=final, current_level__gte=level, race__can_play=True)

            for user in users:
                scoring.score(
                        user,
                        QuestGame,
                        self.get_formula('finalquest-ok'),
                        level=level,
                        level_users=users.count()
                )
                signal_msg = ugettext_noop("received bonus for reaching level {level} in the final quest")
                signals.addActivity.send(sender=None, user_from=user,
                    user_to=user, message=signal_msg,
                    arguments=dict(level=level),
                    game=QuestGame.get_instance()
                )

    def fetch_levels(self):
        levels = []
        for level in xrange(len(self.levels) + 1):
            level_data = {'id': level, 'users': []}
            for user in QuestUser.objects.filter(current_quest=self, current_level=level):
                # Check finalquest bonus amount
                amount = History.objects.filter(user=user.user, formula__name='finalquest-ok').aggregate(sum=Sum('amount'))['sum']
                user.amount = amount
                level_data['users'].append(user)
            levels.append(level_data)
        return levels
