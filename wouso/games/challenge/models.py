from datetime import datetime
from django.db import models
from django.db.models import Q, Max
from core.user.models import UserProfile
from core.qpool.models import Question
from core.game.models import Game
from core import scoring
from core.scoring.models import Formula

# Challenge will use QPool questions

class ChallengeUser(UserProfile):
    """ Extension of the userprofile, customized for challenge """
    
    def can_challenge(self, user):
        user = user.get_extension(ChallengeUser)
        if self.user == user.user:
            # Cannot challenge myself
            return False
        # TODO: implement has_challenged, 1 challenge per day restriction
        # TODO: we should return a reasoning why we cannot challenge
        return True
        
    def can_play(self, challenge):
        return challenge.can_play(self)
        
    def __unicode__(self):
        return unicode(self.user)

class Participant(models.Model):
    user = models.ForeignKey(ChallengeUser)
    start = models.DateTimeField(null=True, blank=True)
    played = models.BooleanField(default=False)
    responses = models.TextField(default='', blank=True, null=True)
    
    @property
    def challenge(self):
        #return Challenge.objects.get(Q(user_from=self)|Q(user_to=self))
        try:
            return Challenge.objects.get(Q(user_from=self)|Q(user_to=self))
        except:
            return None
    
    def __unicode__(self):
        return unicode(self.user)
    
class Challenge(models.Model):
    STATUS = ( 
        ('L', 'Launched'), 
        ('A', 'Accepted'), 
        ('R', 'Refused'), 
        ('P', 'Played')
    )
    user_from = models.ForeignKey(Participant, related_name="user_from")
    user_to = models.ForeignKey(Participant, related_name="user_to")
    date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='L')
    winner = models.ForeignKey(UserProfile, related_name="winner", null=True, blank=True)
    questions = models.ManyToManyField(Question)
        
    @staticmethod
    def create(user_from, user_to):
        """ Assigns questions, and returns the number of assigned q """
        uf, ut = Participant(user=user_from), Participant(user=user_to)
        uf.save(), ut.save()
        
        c = Challenge(user_from=uf, user_to=ut, date=datetime.now())
        c.save()
        # TODO: qpool.get_by_tag()
        return c
    
    def accept(self):
        self.status = 'A'
        self.save()
        
    def refuse(self):
        self.status = 'R'
        self.save()
        
    def cancel(self):
        self.user_from.delete()
        self.user_to.delete()
        self.delete()
        
    def set_played(self, user, responses):
        """ Set user's results """
        if self.user_to.user == user:
            self.user_to.played = True
            self.user_to.responses = responses
        elif self.user_from.user == user:
            self.user_from.played = True
            self.user_from.responses = responses
            
        if self.user_to.played and self.user_from.played:
            self.status = 'P'
            # TODO Trigger resolved and scoring
        self.save()
        
    def can_play(self, user):
        """ Check if user can play this challenge"""
        if self.user_to.user != user and self.user_from.user != user:
            return False
        
        if self.user_to == user:
            if self.played_to:
                return False
        elif self.user_from == user:
            if self.played_from:
                return False
                
        return True
        
    def is_launched(self):
        return self.status == 'L'
    
    def is_runnable(self):
        return self.status == 'A'
        
    def is_refused(self):
        return self.status == 'R'
        
    def __unicode__(self):
        return "%s vs %s (%s) - %s " % (
            str(self.user_from.user), 
            str(self.user_to.user), 
            self.date,
            self.status)

class ChallengeGame(Game):
    """ Each game must extend Game """
    class Meta:
        verbose_name = "Challenge"
        proxy = True
        
    @staticmethod
    def get_active(user):
        """ Return a list of active (runnable) challenges for a user """
        user = user.get_extension(ChallengeUser)
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user=user, played=False))]
        except Participant.DoesNotExist:
            challs = []
        return challs
    
    @staticmethod    
    def get_played(user):
        """ Return a list of played (scored TODO) challenges for a user """
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user=user, played=True))]
        except Participant.DoesNotExist:
            challs = []
        return challs

