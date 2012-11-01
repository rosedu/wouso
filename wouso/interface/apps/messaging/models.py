from datetime import datetime
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from wouso.core.app import App
from wouso.core.user.models import Player
from wouso.interface.activity import signals

class MessagingUser(Player):
    '''extension of the user profile, customized for messages'''

    can_send_message = models.BooleanField(null=False, blank=False, default=True)
    last_message_ts = models.DateTimeField(null=True, blank=False, default=datetime.now)


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
        if self.sender:
            return 'from ' + self.sender.__unicode__() + ' to ' + self.receiver.__unicode__() +\
            ' @ ' + self.timestamp.strftime("%A, %d %B %Y %I:%M %p")
        else:
             return 'from ' + "System" + ' to ' + self.receiver.__unicode__() +\
            ' @ ' + self.timestamp.strftime("%A, %d %B %Y %I:%M %p")
    @classmethod
    def send(kls, sender, receiver, subject, text, reply_to=None):
        # TODO: check cand send
        m = kls()
        if sender:
            sender = sender.get_extension(MessagingUser)
        receiver = receiver.get_extension(MessagingUser)
        m.sender, m.receiver, m.subject = sender, receiver, subject
        m.text = text
        m.reply_to = reply_to
        m.save()
        if sender:
            sender.last_message_ts = datetime.now()
            sender.save()
        signals.messageSignal.send(sender=None, user_from=sender, user_to=receiver, message='', action='message', game=None)


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
class MessageAdmin(admin.ModelAdmin):
    list_filter = ('read', 'sender', 'receiver')
    list_display = ('__unicode__', 'subject', 'text', 'timestamp')

admin.site.register(MessagingUser)
admin.site.register(Message, MessageAdmin)
