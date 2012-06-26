from django.db import models
from django.contrib import admin
from core.user.models import Player
from datetime import datetime

class ChatUser(Player):
    ''' extension of the User object '''

    canCreateRoom = models.BooleanField(null=False, blank=False, default=True)
    lastMessageTS = models.DateTimeField(null=True, blank=False, default=datetime.now)

class ChatRoom(models.Model):
    ''' basic chatroom '''

    name = models.CharField(max_length=128, null=False, blank=False, default=None)
    deletable = models.BooleanField(null=False, blank=False, default=None)
    renameable = models.BooleanField(null=False, blank=False, default=None)

class ChatMessage(models.Model):
    ''' chat message '''

    content = models.CharField(max_length=500, null=False, blank=False, default=None)
    author = models.ForeignKey(ChatUser, null=True, blank=False, default=None)
    destRoom = models.ForeignKey(ChatRoom, null=True, blank=False, default=None)
    timeStamp = models.DateTimeField(null=True, blank=False, default=None)

    def __unicode__(self):
        #return self.author.__unicode__() + ' : ' + self.content + ' @ ' + self.timeStamp.strftime("%A, %d %B %Y %I:%M %p")
        return self.author.__unicode__() + ' : ' + self.content

# admin interface
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatUser)
