import logging
from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import Player

from wouso.games.challenge.models import Challenge
from wouso.interface.top.models import TopUser
from random import randint

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.utils.translation import ugettext_noop, ugettext as _
from django.core.urlresolvers import reverse

# Create your models here.
class GrandChallengeUser(Player):
    """ Extension of the user profile for GrandChallenge """
    lost = models.IntegerField(default="0")

       

class GrandChallenge(Challenge):
    def __init__(self, user_from, user_to):
        self.user_from = user_from
        self.user_to = user_to
        self.__class__.ALL.append(self)
        self.won, self.lost = None, None
        self.active = True


    @classmethod
    def get_challenges(cls):
        return cls.ALL
        
    @classmethod
    def active(cls):
        return filter(lambda c: c.active, cls.ALL)        


    #Din TopUser faci .user => usr = u.user
    #usr.get_profile().get_extenion(..)
    
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
        print self.won, " won"
     
    @classmethod       
    def played_with(cls, user):
        ret = []
        for c in [c for c in cls.ALL if not c.active]:
            if c.user_from == user:
                ret.append(c.user_to)
            elif c.user_to == user:
                ret.append(c.user_from)
        return ret
         
        
    @classmethod
    def play_round(cls, l_w):
    # joc toate provocarile active
    #print Challenge.all;
    
        for c in GrandChallenge.active():
            c.play()
    
    # pentru jucatorii care nu au pierdut de 2 ori
    # generez noi provocari
    #Iulian
        if (l_w == 0):
            all = GrandChallengeGame.eligible(0)
        elif(l_w == 1): 
            all = GrandChallengeGame.eligible(1)
        
    

        while len(all):
        
            u = all[0]
	# print "elig", u
        # nu e respectata# gasesc un jucator cu care nu am mai jucat 
        # si care are acelasi numar de pierdute
        # Iulian
            played = GrandChallenge.played_with(u)
            numbLosser = len(GrandChallengeGame.eligible(1))        
	        
            efm = [eu for eu in all if ((eu.lost == u.lost) and (eu != u) and ( (eu not in played) or (numbLosser == 2)) )]
        
        #print efm
            if not len(efm):
                break
        #print "efm", efm
            try:
                adversar = efm[0]
                all.remove(adversar)
                all.remove(u)
                GrandChallenge(u, adversar)
            except: pass

class GrandChallengeGame(Game):
    """ Each game must extend Game """
    NUM_USERS = 16
    # trebuie o lista cu utilizatorii ramasi in sistem
    # atat pentru verificare start, cat si pentru continuare turneu
    last = None

    round_number = 0;
    ALL = []
    #Iulian - primii 16
    base_query = TopUser.objects.exclude(user__is_superuser=True)
    allUsers = base_query.order_by('-points')[:NUM_USERS]
    
    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "GrandChallenges"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "grandchallenge_index_view" # aici
        super(GrandChallengeGame, self).__init__(*args, **kwargs)

    @staticmethod
    def start(allUsers):
        user_list = allUsers
        last = None
        for user in user_list:
            u = user.user
            u = u.get_profile().get_extension(GrandChallengeUser)
            GrandChallengeGame.ALL.append(u)
            if last is None:
                last = u
            else:
                GrandChallenge(u, last)
                last = None

    @classmethod
    def eligible(cls, result):
        return filter(lambda user: user.lost==result, cls.ALL)
    
    
