# see https://projects.rosedu.org/projects/wousodjango/wiki/CoreModulesScoring

from datetime import datetime
from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import User

class ScoringModel:
    @classmethod
    def add(kls, id, **data):
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
    external_id = models.IntegerField(default=0)
    formula = models.ForeignKey(Formula, blank=True, null=True, default=None)
    coin = models.ForeignKey(Coin)
    amount = models.FloatField(default=0)

