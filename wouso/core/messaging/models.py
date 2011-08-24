from django.db import models
from django.contrib import admin
from wouso.core.user.models import UserProfile
from datetime import datetime

class MessageUser(UserProfile):
    '''extension of the user profile, customized for messages'''
    
    canSendMessage = models.BooleanField(null=False, blank=False, default=True)
    lastMessageTS = models.DateTimeField(null=True, blank=False, default=datetime.now)



class Message(models.Model):
    '''the message itself'''
    
    sender = models.ForeignKey(MessageUser, null=True, blank=False, default=None, related_name='sender')
    receiver = models.ForeignKey(MessageUser, null=True, blank=False, default=None, related_name='receiver')
    timestamp = models.DateTimeField(null=True, blank=False, default=datetime.now)
    subject = models.CharField(max_length=64, null=False, blank=False, default=None)
    text = models.CharField(max_length=1000, null=False, blank=False, default=None)


    def __unicode__(self):
        return 'from ' + self.sender.__unicode__() + ' to ' + self.receiver.__unicode__() +\
        ' @ ' + self.timestamp.strftime("%A, %d %B %Y %I:%M %p")
    
    
    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return None


#admin
admin.site.register(MessageUser)
admin.site.register(Message)
