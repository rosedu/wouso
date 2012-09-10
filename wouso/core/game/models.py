from django.db import models
from django.core.urlresolvers import reverse
from wouso.core.app import App

class Game(models.Model, App):
    """ Generic game class. Each installed application acting like a
    game should extend this class.
    """
    name = models.CharField(max_length=100, primary_key=True)
    short_name = models.CharField(max_length=64, blank=True)
    verbose_name = models.CharField(max_length=128, blank=True)
    url = models.CharField(max_length=64, blank=True)

    @classmethod
    def get_instance(kls):
        """ Return the unique instance of a Game, starting from its
        class model.
        """
        # TODO: check if caching at this level makes a difference, or
        # django's object manager already caches it.
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

    def get_game_absolute_url(self):
        """ Return a tuple for django template system """
        return reverse(self.url) if self.url else ''

    def __unicode__(self):
        return self.name
