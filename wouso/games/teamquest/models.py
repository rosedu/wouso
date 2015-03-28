from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.qpool.models import Question


class TeamQuestUser(Player):
    pass


class TeamQuest(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    questions = models.ManyToManyField(Question)
    registered = models.BooleanField(default=False)


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


class TeamQuestGroup(PlayerGroup):
    pass


class TeamQuestStatus(models.Model):
    group = models.ForeignKey('TeamQuestGroup', null=True, blank=True, related_name='quests')
    quest = models.ForeignKey('TeamQuest', null=True, blank=True, related_name='participants')
    current_level = models.IntegerField(default=0, blank=True)
    started_time = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    finished_time = models.DateTimeField(default=None, blank=True, null=True)
    finished = models.BooleanField(default=False, blank=True)


class TeamQuestInvitation(models.Model):
    pass

class TeamQuestInvitationRequest(models.Model):
    pass

