from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import Player


# Create your models here.
class GrandChallengeUser(Player):
    """ Extension of the user profile for GrandChallenge """
    lost = models.IntegerField(default="0");

    @classmethod
    def eligible(cls, result):
        return filter(lambda u: u.lost==result, u.ALL)

    def played_with(self, cls):
        ret = []
        for c in [c for c in cls.ALL if not c.active]:
            if c.user_from == self:
                ret.append(c.user_to)
            elif c.user_to == self:
                ret.append(c.user_from)
        return ret

class GrandChallenge(models.Model):
    def __init__(self, user_from, user_to):
        self.user_from = user_from
        self.user_to = user_to
        self.__class__.ALL.append(self)
        self.won, self.lost = None, None
        self.active = True

    def get_challenges(self):
        return self.ALL

    def play(self):
        winner = randint(0, 1) == 0 #trebuie generat de joc
        #print " - chall between %s and %s: " % (self.user_from, self.user_to),
        if winner:
            self.won = self.user_from
            self.user_to.lost += 1
        else:
            self.won = self.user_to
            self.user_from.lost += 1
        self.active = False
        #print self.won, " won"

class GrandChallengeGame(Game):
    """ Each game must extend Game """
    NUM_USERS = 16
    
    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "GrandChallenges"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "challenge_index_view" # aici
        super(ChallengeGame, self).__init__(*args, **kwargs)

    def start(self, user_list):
        assert user_list == NUM_USERS
        last = None
        for user in user_list:
            u = user.get_extension(GrandChallengeUser)
            if last is None:
                last = u
            else:
                GrandChallenge(u, last)
                last = None
