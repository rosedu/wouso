from datetime import datetime
from django.db import models
from django.utils.translation import ugettext as _
from wouso.core import signals
from wouso.core.common import App
from wouso.core.user.models import Player

CONSECUTIVE_LIMIT = 12 # in seconds

class MessagingUser(Player):
    """ extension of the user profile, customized for messages """

    can_send_message = models.BooleanField(null=False, blank=False, default=True)
    last_message_ts = models.DateTimeField(null=True, blank=False, default=datetime.now)


class Message(models.Model):
    """ the message itself """
    _CHECK = True

    sender = models.ForeignKey(MessagingUser, null=True, blank=True, default=None, related_name='sent')
    receiver = models.ForeignKey(MessagingUser, blank=False, related_name='received')
    timestamp = models.DateTimeField(blank=True, default=datetime.now)
    subject = models.CharField(max_length=200, null=False, blank=False, default=None)
    text = models.CharField(max_length=1000, null=False, blank=False, default=None)
    read = models.BooleanField(blank=False, default=False)
    archived = models.BooleanField(blank=True, default=False)
    deleted = models.BooleanField(blank=True, default=False)
    reply_to = models.ForeignKey('Message', null=True, default=None, blank=True, related_name='thread_parent')

    def trash(self):
        self.deleted = True
        self.archived = True
        self.save()

    def archive(self):
        self.archived = True
        self.save()

    def unarchive(self):
        self.archived = False
        self.save()

    def set_read(self):
        self.read = True
        self.save()

    def set_unread(self):
        self.read = False
        self.save()

    def __unicode__(self):
        sender = _('System') if not self.sender else self.sender.__unicode__()

        return _(u"from {sender} to {receiver} @ {date}").format(sender=sender,
                                                                       receiver=self.receiver.__unicode__(),
                                                                       date=self.timestamp.strftime("%A, %d %B %Y %I:%M %p"))

    @classmethod
    def disable_check(cls):
        cls._CHECK = False

    @classmethod
    def enable_check(cls):
        cls._CHECK = True

    @classmethod
    def can_send(cls, sender, receiver):
        """
        Check against scripts and spam
        """
        if not sender or not cls._CHECK:
            return True # System message

        sender = sender.get_extension(MessagingUser)
        seconds_since_last = (datetime.now() - sender.last_message_ts).seconds if sender.last_message_ts else 0
        if seconds_since_last < CONSECUTIVE_LIMIT:
            seconds_since_last, sender.last_message_ts, datetime.now()
            return False

        return True


    @classmethod
    def send(cls, sender, receiver, subject, text, reply_to=None):
        if not cls.can_send(sender, receiver):
            return _("Cannot send message.")

        m = cls()
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
        return None


class MessageApp(App):

    @classmethod
    def get_unread_count(cls, request):
        if not request.user.get_profile():
            return -1
        return cls.get_unread_for_user(request.user)

    @classmethod
    def get_unread_for_user(cls, user):
        msg_user = user.get_profile().get_extension(MessagingUser)
        return msg_user.received.filter(read=False).count()
