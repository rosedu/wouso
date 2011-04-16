from django.db import models
from django.db.models import Q, Count
from django.contrib.auth.models import User
import datetime
import wouso.settings as config
from django.forms import ModelForm

class Artifact(models.Model):
    """ Artifact object, now streamline """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=config.MEDIA_ARTIFACTS)
    
    def __unicode__(self):
        return self.name
    
class Message(models.Model):
    """ Private message """
    user_from = models.ForeignKey(User, related_name='user_msg_from')
    user_to = models.ForeignKey(User, related_name='user_msg_to')
    subject = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    date = models.DateTimeField()
    read = models.BooleanField(default=False)
    
    def __unicode__(self):
        # TODO: check unicode subject admin problem
        return "%s - %s : %s" % (self.user_from, self.user_to, self.subject)

""" User Profile used for adding more attributes like: 
        real_name, has_answered_qotd, etc.
    This object can be accesed with User.get_profile().
"""
class UserProfile(models.Model):
    # One to one key to User
    user = models.ForeignKey(User, unique=True)
    # Shouldn't this be a OneToOneField, as per
    # http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    # ?

    # Details
    last_online = models.DateTimeField(null=True)
    points = models.FloatField(default=0)
    has_answered_qotd = models.BooleanField(default=False)   
    # Artifacts
    artifacts = models.ManyToManyField(Artifact, blank=True)
    
    def real_name(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)
        
    def email(self):
        return self.user.email    
    
    def can_challenge(self, profile):
        """ Returns if i can challenge given profile user """ 
        if profile.user == self.user:
            return False
        return True
        
    def get_all_messages(self):
        return Message.objects.filter(Q(user_from=self.user)|Q(user_to=self.user))
        
    def get_in_messages(self):
        return Message.objects.filter(user_to=self.user)
        
    def get_out_messages(self):
        return Message.objects.filter(user_from=self.user)
        
    def get_unread_messages(self):
        return Message.objects.filter(user_to=self.user).filter(read=False).aggregate(count=Count('id'))['count']
        
    def __unicode__(self):
        return self.real_name()


# Hack for having user and user's profile always in sync
def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, User)
