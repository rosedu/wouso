# see https://projects.rosedu.org/projects/wousodjango/wiki/CoreModulesScoring

import logging
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from wouso.core.god import God
from wouso.core.game import get_games
from wouso.core.game.models import Game

class ScoringModel:
    @classmethod
    def add(kls, id, **data):
        if isinstance(id, kls):
            id.save()
        else:
            c = kls.objects.create(id=id, **data)
    
    @classmethod
    def get(kls, id):
        if isinstance(id, kls):
            return id
        try: 
            return kls.objects.get(id=id)
        except kls.DoesNotExist:
            return None
    
    def __str__(self):
        return u'%s' % self.id
            
class Coin(ScoringModel, models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    # The game owner module, or null if is a core coin
    owner = models.ForeignKey(Game, blank=True, null=True)
    name = models.CharField(max_length=100)
    
    def is_core(self):
        return owner is None

class Formula(ScoringModel, models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    formula = models.CharField(max_length=500, default='')
    owner = models.ForeignKey(Game)
    description = models.CharField(max_length=500, default='')

class History(models.Model):
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game, blank=True, null=True, default=None)
    external_id = models.IntegerField(default=0, null=True, blank=True)
    formula = models.ForeignKey(Formula, blank=True, null=True, default=None)
    coin = models.ForeignKey(Coin)
    amount = models.FloatField(default=0)
    
    @staticmethod
    def user_coins(user):
        coins = {}
        for game in get_games():
            hs = list(History.objects.filter(user=user, game=game.get_instance()))
            for h in hs:
                if h.coin.id in coins.keys():
                    coins[h.coin.id] += h.amount
                else:
                    coins[h.coin.id] = h.amount

        return coins

    @staticmethod
    def user_points(user):
        """ :return: a list of (game, points) - distribution of points per source """
        points = {}
        coins = History.user_coins(user)
        for game in get_games():
            pp = {}
            hs = History.objects.filter(user=user, game=game.get_instance())
            for h in hs:
                if h.coin in pp.keys():
                    pp[h.coin] += h.amount
                else:
                    pp[h.coin] = h.amount
            if pp.keys():
                points[game.get_instance().verbose_name] = pp
        # TODO: get points without a game origin
        return points

    def __unicode__(self):
        return "{user} {date}-{formula}[{ext}]: {amount}{coin}".format(user=self.user, date=self.timestamp, formula=self.formula, ext=self.external_id, amount=self.amount, coin=self.coin)

# Hack(?) for keeping User points in sync
""" disable for now
def sync_user_points(sender, instance, **kwargs):
    user = instance.user
    coin = Coin.get('points')
    if instance.coin == coin:
        result = History.objects.filter(user=user,coin=coin).aggregate(total=models.Sum('amount'))
        player = user.get_profile()
        player.points = result['total']
        player.level_no = God.get_level_for_points(player.points)
        player.save()
        logging.debug("Updated %s with %f points, level %d" % (player, player.points, player.level_no))
models.signals.post_save.connect(sync_user_points, History)
models.signals.post_delete.connect(sync_user_points, History)
"""
