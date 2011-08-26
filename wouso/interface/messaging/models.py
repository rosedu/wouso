from django.db import models
from django.contrib import admin
from wouso.core.user.models import UserProfile
from datetime import datetime

class MessagingUser(UserProfile):
    '''extension of the user profile, customized for messages'''
    
    canSendMessage = models.BooleanField(null=False, blank=False, default=True)
    lastMessageTS = models.DateTimeField(null=True, blank=False, default=datetime.now)



class Message(models.Model):
    '''the message itself'''
    
    sender = models.ForeignKey(MessagingUser, null=True, blank=False, default=None, related_name='sender')
    receiver = models.ForeignKey(MessagingUser, null=True, blank=False, default=None, related_name='receiver')
    timestamp = models.DateTimeField(null=True, blank=False, default=datetime.now)
    subject = models.CharField(max_length=64, null=False, blank=False, default=None)
    text = models.CharField(max_length=1000, null=False, blank=False, default=None)


    def __unicode__(self):
        return 'from ' + self.sender.__unicode__() + ' to ' + self.receiver.__unicode__() +\
        ' @ ' + self.timestamp.strftime("%A, %d %B %Y %I:%M %p")

    @classmethod
    def send(kls, sender, receiver, subject, text):
        # TODO: check cand send
        m = kls()
        sender = sender.get_extension(MessagingUser)
        receiver = receiver.get_extension(MessagingUser)
        m.sender, m.receiver, m.subject = sender, receiver, subject
        m.text = text
        m.save()
        sender.lastMessageTS = datetime.now()
        sender.save()

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return None


#admin
admin.site.register(MessagingUser)
admin.site.register(Message)
