__author__ = 'alex'

from piston.handler import BaseHandler
from piston.utils import rc
from wouso.core.game import get_games
from wouso.core.user.models import Player
from wouso.interface.apps import get_apps

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

        return {'first_name': player.user.first_name,
                'last_name': player.user.last_name,
                'points': player.points,
                'race': player.race.name,
                'level_no': player.level_no,
                'email': player.user.email,
                'level': player.level,
        }