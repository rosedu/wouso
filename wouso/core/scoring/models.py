import logging
from datetime import datetime
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User
from wouso.core.game import get_games
from wouso.core.game.models import Game

class ScoringModel:
    """ Generic loose, fail-proof model with add_if_does_not_exist
    and get_if_it_isnt_already_an_instance methods
    """
    @classmethod
    def _cache_key(cls, id):
        return 'SM' + cls.__name__ + '-' + id

    @classmethod
    def add(kls, id, **data):
        if isinstance(id, kls):
            id.save()
            c = id
        elif isinstance(id, dict):
            c = kls.objects.create(**id)
        else:
            c = kls.objects.create(id=id, **data)
        return c

    @classmethod
    def get(kls, id):
        if isinstance(id, kls):
            return id
        if isinstance(id, dict):
            id = id.get('id', '')
        cache_key = kls._cache_key(id)
        if cache_key in cache:
            return cache.get(cache_key)
        try:
            val = kls.objects.get(id=id)
            cache.set(cache_key, val)
            return val
        except kls.DoesNotExist:
            return None

    def __str__(self):
        return u'%s' % self.id


class Coin(ScoringModel, models.Model):
    """ Different scoring categories.

    A special coin is 'points' since is used for ladder and levels.
    """
    id = models.CharField(max_length=100, primary_key=True)
    # The coin owner module, or null if is a core coin
    owner = models.ForeignKey(Game, blank=True, null=True)
    name = models.CharField(max_length=100)
    # If the coin values are forced integers, else using float.
    integer = models.BooleanField(default=False, blank=True)

    def is_core(self):
        """ A coin is a core coin, if it doesn't have an owner """
        return self.owner is None

    def format_value(self, amount):
        if self.integer:
            return int(round(amount))
        return amount

class Formula(ScoringModel, models.Model):
    """ Define the way coin amounts are given to the user, based
    on keyword arguments formulas.

    A formula is owned by a game, or by the system (set owner to None)
    """
    id = models.CharField(max_length=200, primary_key=True)
    definition = models.CharField(max_length=1000, default='')
    owner = models.ForeignKey(Game, null=True, blank=True)
    description = models.CharField(max_length=500, default='')

    @classmethod
    def get(kls, id_string, default_string=None):
        """ Performs a get lookup on the Formula table, if no formula exists
        with the first id_string, returns the formula with the default_string
        id.
        """
        if not default_string:
            return super(Formula, kls).get(id_string)

        try: formula = Formula.objects.get(id=id_string)
        except kls.DoesNotExist:
            formula = super(Formula, kls).get(default_string)
            return formula
        return formula

class History(models.Model):
    """ Scoring history keeps track of scoring events per user, saving
    the details from source to amount.
    """
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game, blank=True, null=True, default=None)
    # this is reserved for further use/debugging
    external_id = models.IntegerField(default=0, null=True, blank=True)
    formula = models.ForeignKey(Formula, blank=True, null=True, default=None)
    coin = models.ForeignKey(Coin)
    amount = models.FloatField(default=0)
    percents = models.IntegerField(default=100)
    # group same kind of bonuses together, using the same formula
    tag = models.CharField(max_length=64, blank=True, null=True)

    @classmethod
    def _cache_key(cls, user, game=None, default=False):
        if default:
            return 'ScoringH-' + str(user.id)
        return 'ScoringHG-' + (game.name if game else '') + '-' + str(user.id)

    @classmethod
    def add(cls, user=None, game=None, **kwargs):
        ret = History.objects.create(user=user, game=game, **kwargs)
        cache.delete(cls._cache_key(user, default=True))
        cache.delete(cls._cache_key(user, game=game))
        return ret

    @staticmethod
    def user_coins(user):
        """ Returns a dictionary of coins and amounts for a specific user. """
        cache_key = History._cache_key(user, default=True)
        if cache_key in cache:
            return cache.get(cache_key)
        allcoins = Coin.objects.all()
        coins = {}
        for coin in allcoins:
            hs = History.objects.filter(user=user, coin=coin).aggregate(total=models.Sum('amount'))
            if hs['total'] is not None:
                coins[coin.id] = coin.format_value(hs['total'])
            else:
                if coin.is_core():
                    coins[coin.id] = 0
        cache.set(cache_key, coins)
        return coins

    @staticmethod
    def user_points(user):
        """ :return: a list of (game, points) - distribution of points per source """
        points = {}
        for game in get_games() + [None]:
            pp = History.user_points_from_game(user, game, zeros=False)
            if pp:
                if game:
                    points[game.get_instance().verbose_name] = pp
                else:
                    points['wouso'] = pp
        return points

    @staticmethod
    def user_points_from_game(user, game, zeros=True):
        # FIXME: add test
        game = game.get_instance() if game else game
        cache_key = History._cache_key(user, game=game)
        if cache_key in cache:
            return cache.get(cache_key)
        hs = History.objects.filter(user=user, game=game)
        pp = {}
        if zeros:
            for c in Coin.objects.all():
                pp[c.id] = 0
        for h in hs:
            pp[h.coin.id] = pp.get(h.coin.id, 0) + h.amount
        cache.set(cache_key, pp)
        return pp

    def delete(self, using=None):
        cls = self.__class__
        cache.delete(cls._cache_key(self.user, default=True))
        cache.delete(cls._cache_key(self.user, game=self.game))
        super(History, self).delete(using=using)

    def __unicode__(self):
        return "{user} {date}-{formula}[{ext}]: {amount}{coin}".format(user=self.user, date=self.timestamp, formula=self.formula, ext=self.external_id, amount=self.amount, coin=self.coin)
