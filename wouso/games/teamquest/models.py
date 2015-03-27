from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup

class TeamQuestUser(Player):
	pass

class TeamQuest(models.Model):
	pass


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
	pass

class TeamQuestInvitation(models.Model):
	pass

class TeamQuestInvitationRequest(models.Model):
	pass
