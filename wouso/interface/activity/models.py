import json
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from wouso.core.game import get_games
from wouso.core.game.models import Game
from wouso.core.user.models import Player
from wouso.interface import logger
from wouso.interface.activity.signals import addActivity

class Activity(models.Model):
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    user_from = models.ForeignKey(Player, related_name='user_from', blank=True, null=True)
    user_to = models.ForeignKey(Player, related_name='user_to', blank=True, null=True)
    message_string = models.CharField(max_length=140)
    arguments = models.CharField(max_length=600)
    game = models.ForeignKey(Game, blank=True, null=True)

    @property
    def message(self):
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
            return (self.game.url, None)
        else:
            return (None, None)

    @classmethod
    def filter_activity(cls, queryset, exclude_others=False, wouso_only=False):
        if wouso_only:
            queryset = queryset.filter(game__isnull=True)
        if exclude_others:
            queryset = queryset.exclude(user_from__race__can_play=False)
        return queryset.order_by('-timestamp')

    @classmethod
    def get_global_activity(cls, exclude_others=True, wouso_only=True):
        """ Return all game activity, ordered by timestamp, newest first
        """
        query = cls.objects.all()
        return cls.filter_activity(query, exclude_others=exclude_others, wouso_only=wouso_only)

    @classmethod
    def get_player_activity(cls, player, **kwargs):
        """
        Return an user's activity.
        """
        query = cls.objects.filter(Q(user_to=player) | Q(user_from=player)).order_by('-timestamp')
        return cls.filter_activity(query)

    @classmethod
    def get_race_activiy(cls, race, **kwargs):
        """
        Return all group activity
        """
        query = cls.objects.filter(Q(user_to__race=race) | Q(user_from__race=race)).distinct()
        return cls.filter_activity(query, **kwargs)

    @classmethod
    def get_group_activiy(cls, group, **kwargs):
        """
        Return all group activity
        """
        query = cls.objects.filter(Q(user_to__playergroup=group) | Q(user_from__playergroup=group)).distinct()
        return cls.filter_activity(query, **kwargs)

    @classmethod
    def delete(cls, game, user_from, user_to, message, arguments):
        """ Note: must be called with the _same_ arguments as the original to work """
        for k in arguments.keys():
            arguments[k] = unicode(arguments[k])
        arguments = json.dumps(arguments)
        cls.objects.filter(game=game, user_from=user_from, user_to=user_to, message_string=message, arguments=arguments).delete()

    def __unicode__(self):
        return u"[%s] %s %s" % (self.game, self.user_from, self.user_to)

def addActivity_handler(sender, **kwargs):
    """ Callback function for addActivity signal """
    a = Activity()
    a.user_from = kwargs['user_from']
    a.user_to = kwargs['user_to']
    a.message_string = kwargs['message']
    args = kwargs.get('arguments', {})
    for k in args.keys():
        args[k] = unicode(args[k])
    a.arguments = json.dumps(args)
    a.game = kwargs['game']
    a.save()

addActivity.connect(addActivity_handler)
