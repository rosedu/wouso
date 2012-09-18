from datetime import datetime, timedelta
from django.utils.translation import ugettext_noop
import logging
from wouso.core.app import App
from models import Activity
from signals import addActivity

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

def challenge_count(player):
    """
     Return the count of challenges played by player.
    """
    games_played = Activity.get_private_activity(player).filter(action__contains='chall').count()

    return games_played;

def consecutive_chall_won(player):
    """
     Return the count of won challenges in a row
    """
    activities = Activity.get_private_activity(player).filter(action__contains='chall').order_by('-timestamp')[:12]
    result = 0;
    for i in activities:
        if i.user_from == player:
            result += 1
        else:
            return result
    return result

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

        if 'chall' in action:
            # Check if number of challenge games is 30*k
            games_played = challenge_count(player)
            if games_played > 0 and mod(games_played, 30) == 0:
                if not player.magic.has_modifier('ach-chall-30'):
                    cls.earn_achievement(player, 'ach-chall-30');

            #Check 10 won challenge games in a row
            if consecutive_chall_won(player) >= 10:
                if not player.magic.has_modifier('ach-chall-won-10'):
                    cls.earn_achievement(player, 'ach-chall-won-10');

        if action == 'seen':
            # Check previous 10 seens
            if consecutive_seens(player, datetime.now()) >= 10:
                if not player.magic.has_modifier('ach-login-10'):
                    cls.earn_achievement(player, 'ach-login-10')

    @classmethod
    def get_modifiers(self):
        return ['ach-login-10', 'ach-chall-30', 'ach-chall-won-10']

def check_for_achievements(sender, **kwargs):
    Achievements.activity_handler(sender, **kwargs)

addActivity.connect(check_for_achievements)
