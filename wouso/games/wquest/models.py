from django.db import models
from django import forms
from django.contrib.auth.models import User
import datetime

class WQuest(models.Model):
    """ Define a timed quest """
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    levels = models.IntegerField(default=0)
    
    def questions(self):
        return Question.objects.filter(quest=self) #order_by(position)!
    
    @staticmethod
    def get_current():
        try:
            quest = WQuest.objects.get(start__lte=datetime.datetime.now(),
                                    end__gte=datetime.datetime.now())
        except WQuest.DoesNotExist:
            quest = None
        return quest
        
    def elapsed(self):
        """ Returns elapsed time """
        return datetime.datetime.now() - self.start
        
    def __unicode__(self):
        if self.title != "":
            return self.title
        return "Q%s" % self.start

class Question(models.Model):
    """ Quest question """
    quest = models.ForeignKey(WQuest)
    text = models.TextField()
    answer = models.TextField()
    difficulty = models.IntegerField(default=0)
    points = models.FloatField(default=0)
    level = models.IntegerField(default=0) # should be unique in a quest
    
    def __unicode__(self):
        return self.text
    
class UserProgress(models.Model):
    """ User's progress in specified quest """
    user = models.ForeignKey(User)
    quest = models.ForeignKey(WQuest)
    points = models.FloatField(default=0)
    finished = models.BooleanField(default=False)
    current_level = models.IntegerField(default=0)
    question = models.ForeignKey(Question, blank=True, null=True)
    
    def check_answer(self, answer):
        """ Check answer and progress. Return answer correctness """
        if not self.finished and answer == self.question.answer:
            self.current_level = self.current_level + 1
            if self.current_level == self.quest.levels:
                self.finished = True
            else:
                self.question = Question.objects.get(quest=self.quest, level=self.current_level)
            self.save()
            return True
        
        return False
    
    @staticmethod
    def get_progress(user, quest):
        """ User progress in quest """
        try:
            progress = UserProgress.objects.get(user=user, quest=quest)
        except UserProgress.DoesNotExist:
            progress = UserProgress(user=user, quest=quest, current_level=0)
            progress.question = Question.objects.get(quest=quest, level=0)
            progress.save()
        
        return progress
        
class QuestForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('answer', )
