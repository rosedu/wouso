from datetime import datetime, timedelta
from django.utils.translation import ugettext_noop
import logging
from wouso.core.app import App
from models import Activity
from signals import addActivity,messageSignal
from wouso.interface.apps.messaging.models import Message
def consecutive_seens(player, timestamp):
    """
     Return the count of consecutive seens for a player, until timestamp
    """
    activities = Activity.get_private_activity(player).filter(action='seen').order_by('-timestamp')[0:100]
    today = timestamp.date()
    for i, activity in enumerate(activities):
        date = activity.timestamp.date()
        if date != today + timedelta(days=-i):
            return i

    return len(activities)
    
def consecutive_qotd_correct(player):
    """
     Return the count of correct qotd in a row
    """
    activities = Activity.get_player_activity(player).filter(action__contains = 'qotd').order_by('-timestamp')[:12]
    result = 0
    for i in activities:
        if 'correct' in i.action:
            result +=1
        else:
            return result
    return result
    
def login_between(time,first,second):
    if time.hour >= first and time.hour < second:
        return True
    return False
    
def unique_users_pm(player,minutes):
    activities = Message.objects.filter(receiver=player,timestamp__gt=datetime.now()-timedelta(minutes=5)).values('sender').distinct()
    return len(activities)
    
def wrong_first_qotd(player):
    activities = Activity.get_player_activity(player).filter(action__contains='qotd')
    if not len(activities) == 1:
        return False
    if activities[0].action == 'qotd-wrong':
        return True
    return False
class Achievements(App):

    @classmethod
    def earn_achievement(cls, player, modifier):
        result = player.magic.give_modifier(modifier)
        if result is not None:
            message = ugettext_noop('earned {artifact}')
            addActivity.send(sender=None, user_from=player, game=None, message=message,
                arguments=dict(artifact=result.artifact)
            )
        else:
            logging.debug('%s would have earned %s, but there was no artifact' % (player, modifier))

    @classmethod
    def activity_handler(cls, sender, **kwargs):
        action = kwargs.get('action', None)
        player = kwargs.get('user_from', None)
        if not action:
            return
        if 'qotd' in action:
            #Check 10 qotd in a row
            if consecutive_qotd_correct(player) >= 10:
                if not player.magic.has_modifier('ach-qotd-10'):
                    cls.earn_achievement(player,'ach-qotd-10')
            #Check for wrong answer the first qotd
            if wrong_first_qotd(player):
                if not player.magic.has_mofifier('ach-bad-start'):
                    cls.earn_achievement(player,'ach-bad-start')
        
        if action == "message":
            #Check the number of unique users who send pm to player in the last m minutes
            if unique_users_pm(kwargs.get('user_to'),30) >=3:
                if not kwargs.get('user_to').magic.has_modifier('ach-popularity'):
                    cls.earn_achievement(kwargs.get('user_to'),'ach-popularity')
        if action in  ("login","seen"):
            #Check login between 2-4 am
            if login_between(kwargs.get('timestamp',datetime.now()),2,4):
                if not player.magic.has_modifier('ach-night-owl'):
                    cls.earn_achievement(player,'ach-night-owl')
            elif login_between(kwargs.get('timestamp',datetime.now()),6,8):
                if not player.magic.has_modifier('ach-early-bird'):
                    cls.earn_achievement(player,'ach-early-bird')
        if action == 'seen':
            # Check previous 10 seens
            if consecutive_seens(player, datetime.now()) >= 10:
                if not player.magic.has_modifier('ach-login-10'):
                    cls.earn_achievement(player, 'ach-login-10')
    @classmethod
    def get_modifiers(self):
        return ['ach-login-10','ach-qotd-10','ach-night-owl','ach-early-bird','ach-popularity', 'ach-bad-start']

def check_for_achievements(sender, **kwargs):
    Achievements.activity_handler(sender, **kwargs)

addActivity.connect(check_for_achievements)
messageSignal.connect(check_for_achievements)
