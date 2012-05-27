import logging

from wouso.core.god import God
from wouso.core.magic.models import PlayerSpellDue, PlayerSpellAmount, PlayerArtifactAmount


class InsufficientAmount(Exception): pass

class MagicManager(object):
    def __init__(self, player):
        self.player = player

    @property
    def spells(self):
        return self.player.playerspelldue_set.all()

    @property
    def spells_cast(self):
        return PlayerSpellDue.objects.filter(source=self)

    @property
    def spells_available(self):
        return PlayerSpellAmount.objects.filter(player=self)

    @property
    def artifact_amounts(self):
        return self.player.playerartifactamount_set

    @property
    def spell_amounts(self):
        return self.player.playerspellamount_set

    def has_modifier(self, modifier):
        """ Check for an artifact with id = modifier
        or for an active spell cast on me with id = modifier
        """
        try:
            return PlayerArtifactAmount.objects.get(player=self.player, artifact__name=modifier)
        except PlayerArtifactAmount.DoesNotExist:
            pass

        try:
            return PlayerSpellDue.objects.filter(player=self.player, spell__name=modifier).count() > 0
        except PlayerSpellDue.DoesNotExist:
            pass
        return False

    def modifier_percents(self, modifier):
        """ Return the percents integer value of given modifier
        """
        percents = 100
        res = PlayerArtifactAmount.objects.filter(player=self.player, artifact__name=modifier)
        for a in res:
            percents += a.amount * a.artifact.percents
            # now add spells to that
        res = PlayerSpellDue.objects.filter(player=self.player, spell__name=modifier)
        for a in res:
            percents += a.spell.percents
        return percents

    def use_modifier(self, modifier, amount):
        """ Substract amount of modifier artifact from players collection.
        If the current amount is less than amount, raise an exception.
        If the amount after substraction is zero, delete the corresponding
        artifact amount object.
        """
        paamount = self.has_modifier(modifier)
        if amount > paamount.amount:
            raise InsufficientAmount()

        paamount.amount -= amount
        if not paamount.amount:
            paamount.delete()
        else:
            paamount.save()
        return paamount

    def give_modifier(self, modifier, amount):
        """ Add given amount to existing, or create new artifact amount
        for the current user.
        """
        if amount <= 0:
            return

        paamount = self.has_modifier(modifier)
        if not paamount:
            artifact = God.get_artifact_for_modifier(modifier, self.player)
            paamount = PlayerArtifactAmount.objects.create(player=self.player, artifact=artifact, amount=amount)
        else:
            paamount.amount += amount
            paamount.save()
        return paamount

    def add_spell(self, spell):
        """ Add a spell to self collection """
        try:
            psamount = PlayerSpellAmount.objects.get(player=self.player, spell=spell)
        except PlayerSpellAmount.DoesNotExist:
            return PlayerSpellAmount.objects.create(player=self.player, spell=spell)
        psamount.amount += 1
        psamount.save()
        return psamount


    def spell_stock(self, spell):
        """ Return the count of spells an user has
        """
        try:
            psa = PlayerSpellAmount.objects.get(player=self, spell=spell)
        except PlayerSpellAmount.DoesNotExist:
            return 0
        return psa.amount

    def cast_spell(self, spell, source, due):
        """ Curse self with given spell from source, for due time. """
        try:
            psamount = PlayerSpellAmount.objects.get(player=source, spell=spell)
            assert psamount.amount > 0
        except (PlayerSpellAmount.DoesNotExist, AssertionError):
            return False

        # Pre-cat God actions: immunity and curse ar done by this
        # check
        if not God.can_cast(spell, source, self.player):
            return False

        try:
            psdue = PlayerSpellDue.objects.create(player=self.player, source=source, spell=spell, due=due)
        except Exception as e:
            logging.exception(e)
            return False
            # Post-cast God action (there are specific modifiers, such as clean-spells
        # that are implemented in God
        God.post_cast(psdue)
        psamount.amount -= 1
        if not psamount.amount:
            psamount.delete()
        else:
            psamount.save()
        return True