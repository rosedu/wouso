from datetime import datetime
from django.db import models
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wouso.core.user.models import Player
from wouso.core.common import App
from wouso.core.config.models import BoolSetting


class ChatUser(Player):
    """ extension of the User object """

    class Meta:
        permissions = (("super_chat_user", "Super chat User."),)

    can_create_room = models.BooleanField(null=False, blank=False, default=True)
    last_message_ts = models.DateTimeField(null=True, blank=False, default=datetime.now)
    can_access_chat = models.BooleanField(null=False, blank=False, default=True)


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

    mess_type = models.CharField(max_length=500, null=False, blank=False, default=None)
    comand = models.CharField(max_length=500, null=False, blank=False, default=None)
    dest_user = models.ForeignKey(ChatUser, null=True, blank=False, default=None, related_name="dest_user_for_special")
    content = models.CharField(max_length=500, null=False, blank=False, default=None)
    author = models.ForeignKey(ChatUser, null=True, blank=False, default=None, related_name="author_of_message")
    dest_room = models.ForeignKey(ChatRoom, null=True, blank=False, default=None)
    time_stamp = models.DateTimeField(null=True, blank=False, default=None)


    def __unicode__(self):
        return self.time_stamp.strftime("%H:%M") + " " + self.author.nickname + ': ' + self.content

    def to_dict(self):
        mesaj = {'room': self.dest_room.name,
                 'user': unicode(self.author.nickname),
                 'text': self.content,
                 'time': self.time_stamp.strftime("%H:%M "),
                 'comand': self.comand,
                 'mess_type': self.mess_type,
                 'dest_user': unicode(self.dest_user.nickname)}
        return mesaj

class Chat(App):
    pass

# admin interface
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatUser)
