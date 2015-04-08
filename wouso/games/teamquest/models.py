import datetime

from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.qpool.models import Question


class TeamQuestUser(Player):
    group = models.ForeignKey('TeamQuestGroup', null=True, blank=True, default=None, related_name='users')

    def is_group_owner(self):
        if self.group is None:
            return False
        return self.group.group_owner == self


class TeamQuestGroup(PlayerGroup):
    group_owner = models.OneToOneField('TeamQuestUser', null=True)

    def is_empty(self):
        return self.users.count() < 1

    @classmethod
    def create(cls, group_owner, name):
        new_group = cls.objects.create(name=name, group_owner=group_owner)
        new_group.users.add(group_owner)
        return new_group

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)
        if user == self.group_owner:
            if self.is_empty() is True:
                self.delete()
            else:
                self.promote_to_group_owner(self.users.all()[0])

    def promote_to_group_owner(self, user):
        self.group_owner = user
        self.save()

    def __unicode__(self):
        return u"%s [%d]" % (self.name, self.users.count())


class TeamQuestLevel(models.Model):
    questions = models.ManyToManyField(Question)
    quest = models.ForeignKey('TeamQuest', null=True, blank=True, related_name='levels')
    bonus = models.IntegerField(default=0)

    @classmethod
    def create(cls, quest, bonus, questions):
        new_level = cls.objects.create(quest=quest, bonus=bonus)
        for q in questions:
            new_level.questions.add(q)
        return new_level

    def add_question(self, question):
        self.questions.add(question)

    def remove_question(self, question):
        if question in self.questions.all():
            self.questions.remove(question)


class TeamQuest(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(default="", max_length=100)

    @classmethod
    def create(cls, title, start_time, end_time, levels):
        new_quest = cls.objects.create(title=title, start_time=start_time, end_time=end_time)
        for l in levels:
            new_quest.levels.add(l)
        return new_quest


class TeamQuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        proxy = True

    user_model = TeamQuestUser

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Team Quest"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        # TODO
        super(TeamQuestGame, self).__init__(*args, **kwargs)


class TeamQuestQuestion(models.Model):
    STATE_CHOICES = {
        ('U', 'UNANSWERED'),
        ('A', 'ANSWERED'),
    }
    LOCK_CHOICES = {
        ('L', 'LOCKED'),
        ('U', 'UNLOCKED'),
    }
    state = models.CharField(default='U', max_length=1, choices=STATE_CHOICES)
    lock = models.CharField(default='L', max_length=1, choices=LOCK_CHOICES)
    level = models.ForeignKey('TeamQuestLevelStatus', null=True, blank=False, related_name='questions')
    question = models.ForeignKey(Question, null=True, blank=False)

    @classmethod
    def create(cls, level, question, lock):
        new_question = cls.objects.create(level=level, question=question, lock=lock)
        return new_question


class TeamQuestLevelStatus(models.Model):
    level = models.ForeignKey('TeamQuestLevel', null=False, blank=False, related_name='actives')
    quest_status = models.ForeignKey('TeamQuestStatus', null=False, blank=False, related_name='levels')

    @classmethod
    def create(cls, status, level):
        new_level_status = cls.objects.create(level=level, quest_status=status)
        lock = 'L'
        # The start level of a quest is the one that has as many questions as the levels of the quest
        # All the questions but the ones on the start level should be locked
        if level.questions.all().count() == level.quest.levels.all().count():
            lock = 'U'
        for question in level.questions.all():
            TeamQuestQuestion.create(level=new_level_status, question=question, lock=lock)
        return new_level_status


class TeamQuestStatus(models.Model):
    group = models.ForeignKey('TeamQuestGroup')
    quest = models.ForeignKey('TeamQuest')
    time_started = models.DateTimeField(default=datetime.datetime.now())
    time_finished = models.DateTimeField(default=None, blank=True, null=True)

    @classmethod
    def create(cls, group, quest):
        new_status = cls.objects.create(group=group, quest=quest)
        for level in quest.levels.all():
            new_status.levels.add(TeamQuestLevelStatus.create(status=new_status, level=level))
        return new_status


class TeamQuestInvitation(models.Model):
    from_group = models.ForeignKey('TeamQuestGroup', null=True, blank=False)
    to_user = models.ForeignKey('TeamQuestUser', null=True, blank=False)

    def __unicode__(self):
        return u"Invitation from %s to %s" % (self.from_group.group_owner, self.to_user)


class TeamQuestInvitationRequest(models.Model):
    to_group = models.ForeignKey('TeamQuestGroup', null=True, blank=False)
    from_user = models.ForeignKey('TeamQuestUser', null=True, blank=False)

    def __unicode__(self):
        return u"Request from %s to %s" % (self.from_user, self.to_group.group_owner)
