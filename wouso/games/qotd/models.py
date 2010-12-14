from django.db import models
from django import forms
from django.contrib.auth.models import User
import datetime

class Question(models.Model):
    text = models.CharField(max_length=200)
    date = models.DateField('day')
    # TODO: add author info, date_added
    
    @staticmethod
    def get_for_today():
        """ TODO: this fails if there are two questions for today, change this """
        try:
            return Question.objects.all().get(date=datetime.date.today())
        except:
            return None
    
    def answers(self):
        try:
            return Answer.objects.all().filter(question=self)
        except:
            return None
        
    def __unicode__(self):
        return "%s - %s" % (self.text, self.date)

class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=200)
    value = models.BooleanField()
    
    def __unicode__(self):
        return self.text

""" Class storing for each user, the qotd history """
class QotdHistory(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    # Store the date, if question is deleted, history remains
    date = models.DateField()
    choice = models.ForeignKey(Answer)
    value = models.BooleanField(default=False)
    
