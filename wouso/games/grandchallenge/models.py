import logging
from django.db import models
from wouso.core.game.models import Game
from wouso.core.user.models import Player

from wouso.games.challenge.models import Challenge
from wouso.interface.top.models import TopUser
from random import randint


# Create your models here.
class GrandChallengeUser(Player):
    """ Extension of the user profile for GrandChallenge """
    lost = models.IntegerField(default="0")

       

class GrandChallenge(models.Model):
   	
    ALL = []
    OUT_PLAY = []

    def __init__(self, user_from, user_to):
        self.user_from = user_from
        self.user_to = user_to
        self.__class__.ALL.append(self)
        self.won, self.lost = None, None
        self.active = True
        self.round_number = None


    @classmethod
    def get_challenges(cls):
        return cls.ALL
        
    @classmethod
    def active(cls):
        return filter(lambda c: c.active, cls.ALL)        


    #Din TopUser faci .user => usr = u.user
    #usr.get_profile().get_extenion(..)
    
    def play(self, round_number):
        winner = randint(0, 1) == 0 #trebuie generat de joc
        print " - chall between %s and %s: " % (self.user_from, self.user_to),
        if winner:
            self.won = self.user_from
            self.lost = self.user_to
            self.user_to.lost += 1
        else:
            self.won = self.user_to
            self.lost = self.user_from
            self.user_from.lost += 1
        self.active = False
        print "won = %s, lost = %s " % (self.won, self.lost)
        self.round_number = round_number       
            
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
    def joaca(cls):
        for c in GrandChallenge.active():
            #numarul rundei...
            c.play(1)
            if(c.lost.lost == 2):
                cls.OUT_PLAY.append(c.lost)
                print c.lost
 
    
    @classmethod 
    def clasament(cls):
        arb_win  = GrandChallengeGame.eligible(0)
        arb_lose = GrandChallengeGame.eligible(1)
        if(len(arb_win) == 1):
            cls.OUT_PLAY.append(arb_win[0]) 
        if(len(arb_lose) == 1):
            cls.OUT_PLAY.append(arb_lose[0])        
        return cls.OUT_PLAY[13:16]
        
    @classmethod
    def play_round(cls, l_w):
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
	        
            efm = [eu for eu in all if ((eu.lost == u.lost) and (eu != u) and ( (eu not in played) or (eu == all[len(all) - 1])) )]
        
            if not len(efm):
                break

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
        self._meta.get_field('url').default = "grandchallenge_index_view"
        super(GrandChallengeGame, self).__init__(*args, **kwargs)


    #schimbat!!!!!!!
    @staticmethod
    def start():
        user_list = GrandChallengeGame.allUsers
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
    
    @classmethod
    def is_final(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        if((len(arb_win) == 1) and (len(arb_lose) == 1)):
            return True
        return False
    
    @classmethod
    def final_round(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        GrandChallenge(arb_win[0], arb_lose[0])

    @classmethod
    def final_second_round(cls):
        GrandChallenge.play_round(1)
        
    @classmethod
    def is_winner(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        if((len(arb_win) == 0) and (len(arb_lose) == 2)):
            return False
        return True
