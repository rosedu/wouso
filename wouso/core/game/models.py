import logging
from django.db import models
from django.core.urlresolvers import reverse
from wouso.core.common import App, CachedItem


class Game(CachedItem, models.Model, App):
    """ Generic game class. Each installed application acting like a
    game should extend this class.
    """
    CACHE_PART = 'name'
    name = models.CharField(max_length=100, primary_key=True)
    short_name = models.CharField(max_length=64, blank=True)
    verbose_name = models.CharField(max_length=128, blank=True)
    url = models.CharField(max_length=64, blank=True)

    @classmethod
    def get_instance(cls):
        """ Return the unique instance of a Game, starting from its class model.
        """
        name = cls.__name__
        return cls.get(name) or cls.add(name)

    @property
    def game(self):
        # TODO: check usage
        name = str(self.__class__.__name__)
        return Game.objects.get(name=name)

    @classmethod
    def get_staff_and_permissions(cls):
        return []

    @classmethod
    def get_formulas(cls):
        """ Returns a list of formulas used by the game """
        return []

    @classmethod
    def get_coins(cls):
        """ Returns a list of game-specific coins (as names)"""
        return []

    def get_game_absolute_url(self):
        """ Return a tuple for django template system """
        return reverse(self.url) if self.url else ''

    def get_real_object(self):
        """ Find a class by name, and instantiate it
        """
        from . import get_games
        for g in get_games():
            if g.__name__ == self.name:
                return g.get_instance()
        logging.error('Could not find game class for self.name %s' % self.name)
        return self

    def __unicode__(self):
        return self.name
