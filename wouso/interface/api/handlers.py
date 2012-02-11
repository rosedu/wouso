__author__ = 'alex'

from piston.handler import BaseHandler
from piston.utils import rc
from wouso.core.game import get_games
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
            return {'count': all, 'type': type}
        elif type in notifs.keys():
            return {'count': notifs[type], 'type': type}
        else:
            return rc.BAD_REQUEST