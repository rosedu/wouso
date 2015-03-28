from django.db import models

from wouso.core.game.models import Game
from wouso.core.user.models import Player, PlayerGroup


class TeamQuestUser(Player):
    group = models.ForeignKey('TeamQuestGroup', null=True, blank=True, default=None, related_name='users')
	
    def is_head(self):
        if self.group is None:
            return False
        return self.group.head == self


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
    head = models.OneToOneField('TeamQuestUser', null=True, blank=False)

    @classmethod
    def create(cls, head, name):
        new_group = cls.objects.create(name=name, head=head)
        new_group.users.add(head)
        head.group = new_group
        head.save()
        return new_group


class TeamQuestStatus(models.Model):
	pass

class TeamQuestInvitation(models.Model):
	pass

class TeamQuestInvitationRequest(models.Model):
	pass
