from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from wouso.games.challenge.models import Challenge
from wouso.games.qotd.models import QotdHistory

class Activity(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    specific_activity = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.specific_activity.__unicode__()

class BaseActivity(models.Model):
    activities = generic.GenericRelation(Activity, related_name='specific_activity')
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now=True)
    name_from = ""
    
    def __unicode__(self):
        return 'general activity: %s %s' % (self.user.get_profile(), self.datetime)

class ChallengeActivity(BaseActivity):
    cuser = models.ForeignKey(User)
    points_from = models.FloatField(default=0)
    points_to = models.FloatField(default=0)
    name_to = ""
    
    def __unicode__(self):
        return 'challenge activity: %s vs %s (%s - %s)' % (self.name_from, self.name_to, self.points_from, self.points_to)
    
class QotdActivity(BaseActivity):
    correct = models.BooleanField(default=False)
    
    def __unicode__(self):
        return 'qotd activity: %s correct? %s' % (self.name_from, self.correct)
    
def challenge_activity_handler(sender, instance, **kwargs):
    if (instance.get_status_display() == 'Played'):
        ca = ChallengeActivity(user = instance.user_from,
                               cuser = instance.user_to,
                               points_from = instance.points_from,
                               points_to = instance.points_to)
        ca.save()
        
        a = Activity(specific_activity=ca)
        a.save()

def qotd_activity_handler(sender, instance, **kwargs):
    qa = QotdActivity(user = instance.user,
                     correct = instance.value)
    qa.save()
    
    a = Activity(specific_activity=qa)
    a.save()

post_save.connect(challenge_activity_handler, sender=Challenge)
post_save.connect(qotd_activity_handler, sender=QotdHistory)