import json
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from wouso.core.decorators import cached_method
from wouso.core.game.models import Game
from wouso.core.user.models import Player
from wouso.interface import logger
from wouso.core.signals import addActivity, addedActivity


class Activity(models.Model):
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user_from = models.ForeignKey(Player, related_name='activity_from', blank=True, null=True)
    user_to = models.ForeignKey(Player, related_name='activity_to', blank=True, null=True)
    message_string = models.CharField(max_length=140, blank=True, null=True)
    arguments = models.CharField(max_length=600)
    game = models.ForeignKey(Game, blank=True, null=True, help_text='Game triggering the activity, none for system activity')

    public = models.BooleanField(default=True, blank=True)
    action = models.CharField(max_length=32, null=True, default=None, blank=True, help_text='Distinguish similar activities')

    @property
    def message(self):
        if not self.message_string:
            return u'action: %s' % self.action

        if self.arguments:
            try:
                arguments = json.loads(self.arguments)
            except Exception as e:
                logger.exception(e)
                arguments = {}
        # emphasize
        for k in arguments.keys():
            arguments[k] = '<strong>%s</strong>' % arguments[k]

        return _(self.message_string).format(**arguments)

    @property
    def game_name(self):
        """ Returns the game name """
        return self.game.verbose_name

    @models.permalink
    def get_game_absolute_url(self):
        """ Returns the game url """
        if self.game:
            return self.game.url, None
        else:
            return None, None

    @classmethod
    def filter_activity(cls, queryset, exclude_others=False, wouso_only=False):
        if wouso_only:
            queryset = queryset.filter(game__isnull=True)
        if exclude_others:
            queryset = queryset.exclude(user_from__race__can_play=False)
        # Kill private activity by default
        queryset = queryset.exclude(public=False)
        return queryset.order_by('-timestamp')

    @classmethod
    def queryset(cls):
        """
        Default queryset
        """
        return cls.objects.select_related('game')

    @classmethod
    def get_global_activity(cls, exclude_others=True, wouso_only=True):
        """ Return all game activity, ordered by timestamp, newest first
        """
        query = cls.queryset()
        return cls.filter_activity(query, exclude_others=exclude_others, wouso_only=wouso_only)

    @classmethod
    def get_player_activity(cls, player, **kwargs):
        """
        Return an user's activity.
        """
        query = cls.queryset().filter(Q(user_to=player) | Q(user_from=player)).order_by('-timestamp')
        return cls.filter_activity(query)

    @classmethod
    def get_race_activity(cls, race, **kwargs):
        """
        Return all group activity
        """
        query = cls.queryset().filter(Q(user_to__race=race) | Q(user_from__race=race)).distinct()
        return cls.filter_activity(query, **kwargs)

    @classmethod
    def get_group_activiy(cls, group, **kwargs):
        """
        Return all group activity
        """
        query = cls.queryset().filter(Q(user_to__playergroup=group) | Q(user_from__playergroup=group)).distinct()
        return cls.filter_activity(query, **kwargs)

    @classmethod
    def get_private_activity(cls, player):
        return cls.queryset().filter(user_from=player, public=False)

    @classmethod
    def delete(cls, game, user_from, user_to, message, arguments):
        """ Note: must be called with the _same_ arguments as the original to work """
        for k in arguments.keys():
            arguments[k] = unicode(arguments[k])
        arguments = json.dumps(arguments)
        cls.objects.filter(game=game, user_from=user_from, user_to=user_to, message_string=message, arguments=arguments).delete()

    @cached_method
    def _get_player(self, id):
        return Player.objects.get(id=id)

    @property
    def player_from(self):
        return self._get_player(self.user_from_id)

    @property
    def player_to(self):
        return self._get_player(self.user_to_id)

    def __unicode__(self):
        return u"#%d" % (self.id)


def save_activity_handler(sender, **kwargs):
    """ Callback function for addActivity signal """
    a = Activity()
    a.user_from = kwargs['user_from']
    a.user_to = kwargs.get('user_to', a.user_from)
    a.message_string = kwargs.get('message', '')
    a.action = kwargs.get('action', None)
    args = kwargs.get('arguments', {})
    for k in args.keys():
        args[k] = unicode(args[k])
    a.arguments = json.dumps(args)
    a.game = kwargs['game']
    a.public = kwargs.get('public', True)
    a.save()
    # Notify others
    addedActivity.send(sender=None, activity=a)


addActivity.connect(save_activity_handler)
