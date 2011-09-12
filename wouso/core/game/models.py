from django.db import models
from wouso.core.app import App

class Game(models.Model, App):
    name = models.CharField(max_length=100, primary_key=True)

    @classmethod
    def get_instance(kls):
        instance, new = kls.objects.get_or_create(name=kls.__name__)
        instance.game = Game.objects.get(name=kls.__name__)
        return instance

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by the game """
        return []

    @classmethod
    def get_coins(kls):
        """ Returns a list of game-specific coins (as names)"""
        return []

    @classmethod
    def get_modifiers(kls):
        """ Return a list of modifiers - as names (this translates to artifact names)
        Player has_modifier checks if the user has an artifact with the modifier id.
        """
        return []

    def __unicode__(self):
        return self.name
