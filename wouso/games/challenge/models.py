from django.db import models
from django.db.models import Q, Max
from django.contrib.auth.models import User
from django import forms
import wouso.gamesettings as config
from random import shuffle
        
class Question(models.Model):
    text = models.CharField(max_length=200)
    chapter = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    
    def answers(self):
        try:
            return Answer.objects.all().filter(question=self)
        except:
            return None
            
    def used_increment(self):
        self.used = self.used + 1
        self.save()
        
    def __unicode__(self):
        return "#%d - chap: %d used: %d" % (self.id, self.chapter, self.used)
    
class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=200)
    value = models.BooleanField(default=False)
    
class Challenge(models.Model):
    STATUS = ( 
        (0, 'Launched'), 
        (1, 'Accepted'), 
        (2, 'Refused'), 
        (3, 'Played')
    )
    user_from = models.ForeignKey(User, related_name="user_from")
    user_to = models.ForeignKey(User, related_name="user_to")
    date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default=0)
    winner = models.ForeignKey(User, related_name="winner", null=True, blank=True)
    points_from = models.FloatField(default=0)
    points_to = models.FloatField(default=0)
    played_from = models.BooleanField(default=False)
    played_to = models.BooleanField(default=False)
    start_from = models.DateTimeField(null=True, blank=True)
    start_to = models.DateTimeField(null=True, blank=True)
    # n questions per challenge
    questions = models.ManyToManyField(Question)
        
    def create(self):
        """ Assigns questions, and returns the number of assigned q """
    
        q = Question.objects.all().aggregate(max_used=Max('used'))
        max_used = q['max_used']
        if max_used == None or max_used == 0:
            max_used = 1        
        max_chapter = config.MAX_CHAPTER
        chapter = config.CURRENT_CHAPTER
        """ Some magic - select questions based on:
            70% being close to the current chapter
            30% being less used
            Feel free to improve the formula
        """
        q_pool = Question.objects.extra(
            select={'rank': '(%d - chapter)/%d * 0.7 + (used / %d) * 0.3' % (chapter, max_chapter, max_used)}
            ).filter(chapter__lte=config.CURRENT_CHAPTER).order_by('rank')
        
        #for q in q_pool: print q, q.rank
        # manually filter; TODO: rethink this
        questions = [q for q in q_pool if float(q.rank) <= 0.5]
        # shuffle
        shuffle(questions)
        # take only first five
        limit = config.CHALLENGE_COUNT
        for q in questions:
            #print q, q.rank
            self.questions.add(q)
            # Update used
            q.used_increment()
            limit -= 1
            if limit <= 0:
                break
                
        # Check if we had enough questions
        if limit == 0:
            return True
            
        # TODO: raise an InsufficientQuestions error
        return False
    
    @staticmethod
    def get_active_challenges(user):
        try:
            chall = Challenge.objects.filter(
                Q(user_to=user, played_to=False) | Q(user_from=user, played_from=False))
        except Challenge.DoesNotExist:
            chall = []
        return chall
    
    @staticmethod
    def get_played_challenges(user):
        try:
            chall = Challenge.objects.filter(
                Q(user_to=user, played_to=True) | Q(user_from=user, played_from=True))
        except Challenge.DoesNotExist:
            chall = []
        return chall
    
    def accept(self):
        self.status = 1
        self.save()
        
    def refuse(self):
        self.status = 2
        self.save()
        
    def cancel(self):
        self.delete()
        
    def set_played(self, user, points):
        """ Set user's results """
        if self.user_to == user:
            self.played_to = True
            self.points_to = points
        elif self.user_from == user:
            self.played_from = True
            self.points_from = points
            
        if self.played_to and self.played_from:
            self.status = 3
        self.save()
        
    def can_play(self, user):
        """ Check if user can play """
        if self.user_to != user and self.user_from != user:
            return False
        
        if self.user_to == user:
            if self.played_to:
                return False
        elif self.user_from == user:
            if self.played_from:
                return False
                
        return True
        
    def is_launched(self):
        return self.status == '0'
    
    def is_runnable(self):
        return self.status == '1'
        
    def __unicode__(self):
        return "%s vs %s (%s) - %s " % (
            self.user_from.get_profile(), 
            self.user_to.get_profile(), 
            self.date, 
            Challenge.STATUS[int(self.status)][1])

