from datetime import datetime
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from wouso.core.app import App
from wouso.core.user.models import Player

class MessagingUser(Player):
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
    read = models.BooleanField(null=False, blank=False, default=False)
    reply_to = models.ForeignKey('Message', null=True, default=None, blank=True, related_name='thread_parent')

    def __unicode__(self):
        return 'from ' + self.sender.__unicode__() + ' to ' + self.receiver.__unicode__() +\
        ' @ ' + self.timestamp.strftime("%A, %d %B %Y %I:%M %p")

    @classmethod
    def send(kls, sender, receiver, subject, text, reply_to=None):
        # TODO: check cand send
        m = kls()
        sender = sender.get_extension(MessagingUser)
        receiver = receiver.get_extension(MessagingUser)
        m.sender, m.receiver, m.subject = sender, receiver, subject
        m.text = text
        m.reply_to = reply_to
        m.save()
        sender.lastMessageTS = datetime.now()
        sender.save()

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from wouso.interface.apps.messaging.views import header_link
            return header_link(request)
        return dict(text=_('Messages'), link='')

class MessageApp(App):

    @classmethod
    def get_unread_count(kls, request):
        if not request.user.get_profile():
            return -1
        msg_user = request.user.get_profile().get_extension(MessagingUser)
        return Message.objects.filter(receiver=msg_user).filter(read=False).count()

#admin
admin.site.register(MessagingUser)
admin.site.register(Message)
