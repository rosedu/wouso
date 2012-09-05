from django.db import models
from django.contrib import admin
from core.user.models import Player
from datetime import datetime
from django.utils.translation import ugettext as _

from wouso.core.app import App
from django.core.urlresolvers import reverse
from wouso.core.config.models import BoolSetting
from wouso.core.user.models import *


class ChatUser(Player):
    ''' extension of the User object '''

    class Meta:
        permissions = (("super_chat_user", "Super chat User."),)

    canCreateRoom = models.BooleanField(null=False, blank=False, default=True)
    lastMessageTS = models.DateTimeField(null=True, blank=False, default=datetime.now)



class ChatRoom(models.Model):
    ''' basic chatroom '''

    def __init__(self, *args, **kwargs):
        super(ChatRoom, self).__init__(*args, **kwargs)
        self.DoesNotExist = None

    name = models.CharField(max_length=128, null=False, blank=False, default=None)
    deletable = models.BooleanField(null=False, blank=False, default=None)
    renameable = models.BooleanField(null=False, blank=False, default=None)

    participants = models.ManyToManyField('ChatUser', blank=True, related_name='participant')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    def __unicode__(self):
        return self.name

class ChatMessage(models.Model):
    ''' chat message '''

    messType = models.CharField(max_length=500, null=False, blank=False, default=None)
    comand = models.CharField(max_length=500, null=False, blank=False, default=None)
    content = models.CharField(max_length=500, null=False, blank=False, default=None)
    author = models.ForeignKey(ChatUser, null=True, blank=False, default=None)
    destRoom = models.ForeignKey(ChatRoom, null=True, blank=False, default=None)
    timeStamp = models.DateTimeField(null=True, blank=False, default=None)


    def __unicode__(self):
        #return self.author.__unicode__() + ' : ' + self.content + ' @ ' + self.timeStamp.strftime("%A, %d %B %Y %I:%M %p")
        return self.author.user.username + ' : ' + self.content

class Chat(App):

    @classmethod
    def get_header_link(kls, request):
        if BoolSetting.get('disable-Chat').get_value():
            return {}
        url = reverse('wouso.interface.chat.views.index')
        player = request.user.get_profile() if request.user.is_authenticated() else None
        count = 0

        return dict(link=url, text=_('Chat'), count=count)


# admin interface
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatUser)
