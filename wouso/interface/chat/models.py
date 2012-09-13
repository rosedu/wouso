from datetime import datetime
from django.db import models
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wouso.core.user.models import Player
from wouso.core.app import App
from wouso.core.config.models import BoolSetting


class ChatUser(Player):
    """ extension of the User object """

    class Meta:
        permissions = (("super_chat_user", "Super chat User."),)

    canCreateRoom = models.BooleanField(null=False, blank=False, default=True)
    lastMessageTS = models.DateTimeField(null=True, blank=False, default=datetime.now)
    canAccessChat = models.BooleanField(null=False, blank=False, default=True)


class ChatRoom(models.Model):
    """ basic chatroom """

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

    @classmethod
    def create(cls, roomName, deletable=False, renameable=False):
        """ creates a new chatroom and saves it """
        newRoom = cls(name=roomName, deletable=deletable, renameable=renameable)
        newRoom.save()
        return newRoom

class ChatMessage(models.Model):
    """ chat message """

    messType = models.CharField(max_length=500, null=False, blank=False, default=None)
    comand = models.CharField(max_length=500, null=False, blank=False, default=None)
    destUser = models.ForeignKey(ChatUser, null=True, blank=False, default=None, related_name="dest_user_for_special")
    content = models.CharField(max_length=500, null=False, blank=False, default=None)
    author = models.ForeignKey(ChatUser, null=True, blank=False, default=None, related_name="author_of_message")
    destRoom = models.ForeignKey(ChatRoom, null=True, blank=False, default=None)
    timeStamp = models.DateTimeField(null=True, blank=False, default=None)


    def __unicode__(self):
        return self.timeStamp.strftime("%H:%M") + " " + self.author.nickname + ': ' + self.content

class Chat(App):

    @classmethod
    def get_header_link(kls, request):
        if BoolSetting.get('disable-Chat').get_value():
            return {}
        url = reverse('wouso.interface.chat.views.index')
        count = 0

        return dict(link=url, text=_('Chat'), count=count)


# admin interface
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatUser)
