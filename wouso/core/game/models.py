from django.db import models
from django.core.urlresolvers import reverse
from django.core.cache import cache
from wouso.core.common import App


class Game(models.Model, App):
    """ Generic game class. Each installed application acting like a
    game should extend this class.
    """
    name = models.CharField(max_length=100, primary_key=True)
    short_name = models.CharField(max_length=64, blank=True)
    verbose_name = models.CharField(max_length=128, blank=True)
    url = models.CharField(max_length=64, blank=True)

    @classmethod
    def _cache_key(cls, name):
        return 'Game-' + name

    @classmethod
    def get_instance(cls):
        """ Return the unique instance of a Game, starting from its
        class model.
        """
        cache_key = cls._cache_key(cls.__name__)
        if cache_key in cache:
            return cache.get(cache_key)
        instance, new = cls.objects.get_or_create(name=cls.__name__)
        instance.game = Game.objects.get(name=cls.__name__)
        cache.set(cache_key, instance)
        return instance

    def save(self, **kwargs):
        cache_key = self.__class__._cache_key(self.__class__.__name__)
        cache.set(cache_key, self)
        super(Game, self).save(**kwargs)

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

    def __unicode__(self):
        return self.name
