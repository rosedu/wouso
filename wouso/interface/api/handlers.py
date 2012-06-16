from wouso.interface.top.models import TopUser

__author__ = 'alex'

from piston.handler import BaseHandler
from piston.utils import rc
from wouso.core.user.templatetags.user import player_avatar
from wouso.core.game import get_games
from wouso.core.user.models import Player
from wouso.core.magic.models import Spell
from wouso.core.god import God
from wouso.interface.apps import get_apps

class ApiRoot(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request):
        base = 'http://%s' % request.get_host()
        fullpath = request.get_full_path()
        if '?' in fullpath:
            query = fullpath[fullpath.rindex('?'):]
        else:
            query = ''

        api = {
            'Info': '%s/api/info/%s' % (base, query),
            'Notifications': '%s/api/notifications/all/%s' % (base, query),
        }
        return api

class NotificationsHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, type):
        notifs = {}
        for app in get_apps():
            notifs[app.name()] = app.get_unread_count(request)
        for game in get_games():
            notifs[game.name()] = game.get_unread_count(request)

        all = sum(notifs.values())

        if type == 'all':
            return {'count': all, 'type': type, 'types': notifs.keys()}
        elif type in notifs.keys():
            return {'count': notifs[type], 'type': type}
        else:
            return rc.BAD_REQUEST

class InfoHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request):
        try:
            player = request.user.get_profile()
        except Player.DoesNotExist:
            return rc.NOT_FOUND

        level = {
            'name': player.level.name,
            'title': player.level.title,
            'image': player.level.image,
            'id': player.level.id,
        } if player.level else {}

        group = player.groups.all()[0].name if player.groups.count() else None
        gold = player.coins['gold'] if 'gold' in player.coins.keys() else 0
        topuser = player.get_extension(TopUser)

        return {'first_name': player.user.first_name,
                'last_name': player.user.last_name,
                'email': player.user.email,
                'avatar': player_avatar(player),
                'points': player.points,
                'gold': gold,
                'race': player.race_name,
                'group': group,
                'level_no': player.level_no,
                'level': level,
                'level_progress': God.get_level_progress(player),
                'rank': topuser.position,
        }

class BazaarHandler(BaseHandler):
    methods_allowed = ('GET',)
    object_name = 'spells'

    def get_queryset(self, user=None):
        return Spell.objects.all()

    def read(self, request):
        try:
            player = request.user.get_profile()
        except Player.DoesNotExist:
            return rc.NOT_FOUND

        return {self.object_name: self.get_queryset(user=player)}

class BazaarInventoryHandler(BazaarHandler):
    def get_queryset(self, user=None):
        return user.spells_available