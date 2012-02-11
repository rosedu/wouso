__author__ = 'alex'

from piston.handler import BaseHandler

class NotificationsHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, type):
        return { 'count': 0, 'type': type}