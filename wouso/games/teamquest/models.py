from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup


class TeamQuestUser(Player):
    group = models.ForeignKey('TeamQuestGroup', null=True, blank=True, default=None, related_name='users')
	
    def is_head(self):
        return self.group.head == self


class TeamQuest(models.Model):
	pass

class TeamQuestGame(Game):
	pass


class TeamQuestGroup(PlayerGroup):
	head = models.OneToOneField('TeamQuestUser', null=False, blank=False)


class TeamQuestStatus(models.Model):
	pass

class TeamQuestInvitation(models.Model):
	pass

class TeamQuestInvitationRequest(models.Model):
	pass
