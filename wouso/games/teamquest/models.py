from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup

class TeamQuestUser(Player):
	pass

class TeamQuest(models.Model):
	pass

class TeamQuestGame(Game):
	pass

class TeamQuestGroup(PlayerGroup):
	pass

class TeamQuestStatus(models.Model):
	pass

class TeamQuestInvitation(models.Model):
	pass

class TeamQuestInvitationRequest(models.Model):
	pass
