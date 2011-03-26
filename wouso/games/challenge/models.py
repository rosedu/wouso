import logging
from datetime import datetime
from random import shuffle
import pickle as pk
from django.db import models
from django.db.models import Q, Max
from core.user.models import UserProfile
from core.qpool.models import Question
from core.qpool import get_questions_with_tags
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
        ('P', 'Played'),
        ('D', 'Draw'),
    )
    user_from = models.ForeignKey(Participant, related_name="user_from")
    user_to = models.ForeignKey(Participant, related_name="user_to")
    date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='L')
    winner = models.ForeignKey(ChallengeUser, related_name="winner", null=True, blank=True)
    questions = models.ManyToManyField(Question)
        
    @staticmethod
    def create(user_from, user_to):
        """ Assigns questions, and returns the number of assigned q """
        uf, ut = Participant(user=user_from), Participant(user=user_to)
        uf.save(), ut.save()
        
        c = Challenge(user_from=uf, user_to=ut, date=datetime.now())
        c.save()
        
        questions = [q for q in get_questions_with_tags('challenge')]
        shuffle(questions)
        # TODO: better question selection
        limit = 5
        for q in questions:
            c.questions.add(q)
            limit -= 1
            if limit <= 0: break
        return c
    
    def accept(self):
        self.status = 'A'
        self.save()
        
    def refuse(self):
        self.status = 'R'
        self.save()
        
    def cancel(self):
        self.delete()
        
    def played(self):
        """ Both players have played, save and score """
        self.user_to.points = self.calculate_points(pk.loads(str(self.user_to.responses)))
        self.user_from.points = self.calculate_points(pk.loads(str(self.user_from.responses)))
        if self.user_to.points > self.user_from.points:
            result = (self.user_to, self.user_from)
        elif self.user_from.points > self.user_from.points:
            result = (self.user_from, self.user_to)
        else: #draw game
            result = 'draw'
            
        if result == 'draw':
            self.status = 'D'
            scoring.score(self.user_to.user, ChallengeGame, 'chall-draw')
            scoring.score(self.user_from.user, ChallengeGame, 'chall-draw')
        else:
            self.status = 'P'
            self.user_won, self.user_lost = result
            self.winner = self.user_won.user
            scoring.score(self.user_won.user, ChallengeGame, 'chall-won', 
                external_id=self.id, points=self.user_won.points, points2=self.user_lost.points)
            scoring.score(self.user_lost.user, ChallengeGame, 'chall-lost',
                external_id=self.id, points=self.user_lost.points, points2=self.user_lost.points)
        
        self.save()
    
    def calculate_points(self, responses):
        points = 0
        for r, v in responses.iteritems():
            checked = missed = 0
            q = Question.objects.get(id=r)
            for a in q.answers.all():
                if a.correct:
                    if a.id in v:
                        checked += 1
                    else:
                        missed += 1
                elif a.id in v:
                    missed += 1
            points += float(checked) / q.answers.count()
        return points
        
    def set_played(self, user, responses):
        """ Set user's results """
        if self.user_to.user == user:
            user_played = self.user_to
        elif self.user_from.user == user:
            user_played = self.user_from
        else:
            logging.error("Invalid user")
            return
        
        user_played.played = True
        user_played.responses = pk.dumps(responses)
        user_played.save()
            
        if self.user_to.played and self.user_from.played:
            self.played()
            
        return {'points': self.calculate_points(responses)}
        
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
                
        return self.is_runnable()
        
    def is_launched(self):
        return self.status == 'L'
    
    def is_runnable(self):
        return self.status == 'A'
        
    def is_refused(self):
        return self.status == 'R'
        
    def __unicode__(self):
        return "%s vs %s (%s) - %s [%d] " % (
            str(self.user_from.user), 
            str(self.user_to.user), 
            self.date,
            self.status,
            self.questions.count())

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
        
    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        chall_game = kls.get_instance()
        fs.append(Formula(id='chall-won', formula='points=3', 
            owner=chall_game.game, 
            description='Points earned when winning a challenge')
        )
        fs.append(Formula(id='chall-lost', formula='points=-1', 
            owner=chall_game.game, 
            description='Points earned when losing a challenge')
        )
        fs.append(Formula(id='chall-draw', formula='points=1', 
            owner=chall_game.game, 
            description='Points earned when drawing a challenge')
        )
        return fs

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return None


# Hack for having participants in sync
def challenge_post_delete(sender, instance, **kwargs):
    """ For some reason, this is called twice. Needs investigantion
    Also, in django devele, on_delete=cascade will fix this hack
    """
    try:
        instance.user_from.delete()
        instance.user_to.delete()
    except: pass
models.signals.post_delete.connect(challenge_post_delete, Challenge)

