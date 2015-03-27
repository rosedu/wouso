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
	pass


class TeamQuestGroup(PlayerGroup):
    head = models.OneToOneField('TeamQuestUser', null=True, blank=False)

    @property
    def members(self):
        return [p.get_extension(TeamQuestUser) for p in self.users.all()]

    @property
    def members_except_first(self):
        return [p.get_extension(TeamQuestUser) for p in self.users.all()[1:]]

    def is_empty(self):
        return self.users.count() < 1

    @classmethod
    def create(cls, head, name):
        new_group = cls.objects.create(name=name, head=head)
        new_group.users.add(head)
        return new_group

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)
        if user is self.head:
            if self.is_empty() is True:
                self.delete()
            else:
                self.promote_to_head(self.members[0])
                self.save()

    def promote_to_head(self, user):
        self.head = user
        self.head.save()

    def __unicode__(self):
        return u"%s [%d]" % (self.name, self.users.count())


class TeamQuestStatus(models.Model):
    pass

class TeamQuestInvitation(models.Model):
    from_group = models.ForeignKey('TeamQuestGroup', null=True, blank=False)
    to_user = models.ForeignKey('TeamQuestUser', null=True, blank=False)

    def __unicode__(self):
        return u"Invitation from %s to %s" % (self.from_group.head, self.to_user)


class TeamQuestInvitationRequest(models.Model):
    to_group = models.ForeignKey('TeamQuestGroup', null=True, blank=False)
    from_user = models.ForeignKey('TeamQuestUser', null=True, blank=False)

    def __unicode__(self):
        return u"Request from %s to %s" % (self.from_user, self.to_group.head)
