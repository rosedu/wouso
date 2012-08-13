import logging
import urllib, urllib2
from django.db import models
from django.conf import settings
from wouso.core.user.models import Player

C2DM_URL = 'https://android.apis.google.com/c2dm/send'

class Device(models.Model):
    player = models.ForeignKey(Player)
    registered = models.DateTimeField(auto_now_add=True, editable=False)
    registration_id = models.CharField(max_length=140)

    def send_message(self, collapse_key='', **kwargs):
        values = {
            'registration_id': self.registration_id,
            'collapse_key': collapse_key,
        }

        for key,value in kwargs.iteritems():
            values['data.%s' % key] = value

        headers = {
            'Authorization': 'GoogleLogin auth=%s' % settings.C2DM_AUTH_TOKEN,
        }

        try:
            params = urllib.urlencode(values)
            request = urllib2.Request(C2DM_URL, params, headers)

            response = urllib2.urlopen(request)
            result = response.read()

            parts = result.split('=')

            if 'Error' in parts:
                #if result[1] == 'InvalidRegistration' or result[1] == 'NotRegistered':
                raise Exception(result[1])
        except urllib2.URLError:
            return False
        except Exception as error:
            return False

    def __unicode__(self):
        return 'Device #%d' % self.id

def register_device(player, registration_id):
    """ Register a new device to the given player
    """
    device = Device.objects.create(player=player, registration_id=registration_id)
    device.send_message(payload='Registered')

def notify_user(player, message, collapse_key='wouso'):
    """ Send push notifications to all devices registered to tis user
    """
    for d in player.device_set.all():
        d.send_message(collapse_key=collapse_key, payload=message)