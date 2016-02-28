import logging
from datetime import datetime, timedelta
from django.utils.translation import ugettext_noop
from core import scoring
from core.scoring.sm import score
from wouso.core.common import App
from wouso.core.user.models import Player
from wouso.core.scoring.models import History
from wouso.interface.apps.messaging.models import Message
from wouso.games.challenge.models import Challenge
from wouso.core.magic.models import PlayerSpellDue, SpellHistory, Spell
from models import Activity
from wouso.core.signals import addActivity, messageSignal


def consecutive_days_seen(player, timestamp):
    """
     Return the count of consecutive seens for a player, until timestamp
    """

    # The maximum number of seens in the last 15 days is 24 * 15 ( we have a new 'seen' activity each hour ).
    maximum_times_seen = 15 * 24

    activities = Activity.get_private_activity(player).filter(action='seen').order_by('-timestamp')[0:maximum_times_seen]

    last_day = timestamp.date()
    consecutive_days = 1

    for i, activity in enumerate(activities):
        date = activity.timestamp.date()

        if date == last_day + timedelta(days=-1):
            last_day = date
            consecutive_days = consecutive_days + 1
        elif last_day - date >= timedelta(days=2):
            break

    return consecutive_days


def consecutive_qotd_correct(player):
    """
     Return the count of correct qotd in a row
     Maximum: 10 (last ten)
    """
    activities = Activity.get_player_activity(player).filter(action__contains='qotd').order_by('-timestamp')[:10]
    result = 0
    for i in activities:
        if 'correct' in i.action:
            result += 1
        else:
            return result
    return result


def login_between(time, first, second):
    if first <= time.hour < second:
        return True
    return False


def login_at_start(player, start_day, start_month):
    # Get player's first login
    first_seen = Activity.objects.filter(action__contains='login', user_to=player).order_by('timestamp')[:1]
    month = first_seen[0].timestamp.month
    day = first_seen[0].timestamp.day
    if day == start_day and month == start_month:
        return True

    return False


def login_between_count(player, first, second):
    activities = Activity.objects.filter(action__contains='seen', user_to=player)
    activities = filter(lambda x: first <= x.timestamp.hour < second, activities)
    return len(activities)


def unique_users_pm(player, minutes):
    """
     Return the count of distinct source messages
    """
    activities = Message.objects.filter(receiver=player,
                                        timestamp__gt=datetime.now() - timedelta(minutes=minutes)
    ).values('sender').distinct().count()
    return activities


def wrong_first_qotd(player):
    """
     Check if the first answer to qotd was a wrong answer.
    """
    activities = Activity.get_player_activity(player).filter(action__contains='qotd')
    if not activities.count() == 1:
        return False
    if activities[0].action == 'qotd-wrong':
        return True
    return False


def challenge_count(player, days=None):
    """
     Return the count of challenges played by player in the last x _days_.
     All challenges if days == None
    """
    if not days:
        return Activity.get_player_activity(player).filter(action__contains='chall').count()
    start = datetime.now() - timedelta(days=days)
    return Activity.get_player_activity(player).filter(
        action__contains='chall', timestamp__gte=start).count()


def first_seen(player):
    """
    Return the number of days passed between the current time and the first time
    the player logged in
    """
    first_seen = Activity.objects.filter(action='seen', user_to=player).order_by('timestamp')[:1]
    if first_seen.count() > 0:
        return (datetime.now() - first_seen[0].timestamp).days
    return -1  # user has not logged in ever


def consecutive_chall_won(player):
    """
     Return the count of won challenges in a row
     Maximum: 10 (last ten)
    """
    activities = Activity.get_player_activity(player).filter(action__contains='chall').order_by('-timestamp')[:10]
    result = 0
    for i in activities:
        if 'won' in i.action and i.user_from.id == player.id:
            result += 1
        else:
            return result

    return result


def check_for_god_mode(player, days, chall_min):
    """
    Return true if the player won all challenges and answerd all qotd 'days' days in a row witn a minimum of 'chall_min' challenges
    """
    qotd_list = Activity.objects.all().filter(user_from=player, action__contains="qotd").order_by('-timestamp')
    if len(qotd_list) == 0:
        return False
    if qotd_list[0].action == 'qotd-wrong':
        return False  # Last qotd was incorrect no point to check any further

    last_time = qotd_list[0].timestamp.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
        days=1)  # The day when the latest qotd was ok
    first_time = last_time - timedelta(days=days)  # The earlyest day to check

    chall_won = Activity.objects.all().filter(user_from=player, action='chall-won', timestamp__gte=first_time).exclude(
        timestamp__gte=last_time).count()
    chall_lost = Activity.objects.all().filter(user_to=player, action='chall-won', timestamp__gte=first_time).exclude(
        timestamp__gte=last_time).count()
    qotd_ok = Activity.objects.all().filter(user_from=player, action='qotd-correct', timestamp__gte=first_time).exclude(
        timestamp__gte=last_time).count()

    if chall_won >= chall_min and chall_lost == 0 and qotd_ok == days:
        return True
    return False


def refused_challenges(player):
    """
     Return the count of refused challenges in the last week
    """
    start = datetime.now() + timedelta(days=-7)
    return Activity.get_player_activity(player).filter(action__contains='chall-refused', timestamp__gte=start,
                                                       user_from=player).count()


def challenges_played_today(player):
    """
     Return the count of challenges played today
    """
    today = datetime.now().date()
    activities = Activity.get_player_activity(player).filter(action__contains='chall', timestamp__gte=today)
    result = 0
    for a in activities:
        if not 'refused' in a.action:
            result += 1
    return result


def get_chall_score(arguments):
    if not arguments:
        return 0
    if "id" in arguments:
        chall = Challenge.objects.get(pk=arguments["id"])
        return max(chall.user_from.score, chall.user_to.score)
    else:
        return 0


def get_challenge_time(arguments):
    """
     Return the number of seconds spent by the winner.
    """
    if not arguments:
        return 0

    if "id" in arguments:
        chall = Challenge.objects.get(pk=arguments["id"])
        if chall.user_from.user == chall.winner:
            return chall.user_from.seconds_took
        else:
            return chall.user_to.seconds_took
    else:
        return 0


def spell_count(player):
    """
     Return the number of spells casted on player simultaneously
    """
    today = datetime.now().date()
    return PlayerSpellDue.objects.filter(player=player, due__gte=today).count()


def spent_gold(player):
    """
        Return the amount of gold spent on spells
    """
    activity = SpellHistory.objects.filter(type='b', user_from=player)
    cost = 0
    for a in activity:
        cost += a.spell.price

    return cost


def gold_amount(player):
    """
     Return player's amount of gold
    """
    coins = History.user_coins(player)
    return coins['gold']


def used_all_spells(player, mass):
    """
     Return True if player used all non-mass spells if mass is False,
     or True if player used all mass spells if mass is True.
    """
    all_spells = Spell.objects.filter(mass=mass)
    magic_activity = SpellHistory.objects.filter(user_from=player, type='u')
    used_spells = [m.spell for m in magic_activity if m.spell.mass == mass]

    for s in all_spells:
        if not s in used_spells:
            return False
    return True


class Achievements(App):
    @classmethod
    def earn_achievement(cls, player, modifier):
        result = player.magic.give_modifier(modifier)
        if result is not None:
            message = ugettext_noop('earned {artifact}')
            action_msg = 'earned-ach'
            addActivity.send(sender=None, user_from=player, game=None, message=message,
                             arguments=dict(artifact=result.artifact), action=action_msg
            )
            Message.send(sender=None, receiver=player, subject="Achievement", text="You have just earned " + modifier)
        else:
            logging.debug('%s would have earned %s, but there was no artifact' % (player, modifier))

    @classmethod
    def activity_handler(cls, sender, **kwargs):
        action = kwargs.get('action', None)
        player = kwargs.get('user_from', None)

        if player:
            player = player.get_extension(Player)

        if not action:
            return

        if 'qotd' in action:
            # Check 10 qotd in a row
            if consecutive_qotd_correct(player) >= 10:
                if not player.magic.has_modifier('ach-qotd-10'):
                    cls.earn_achievement(player, 'ach-qotd-10')

        if 'chall' in action:
            # Check if number of challenge games is >= 100
            games_played = challenge_count(player)
            if games_played >= 100:
                if not player.magic.has_modifier('ach-chall-100'):
                    cls.earn_achievement(player, 'ach-chall-100')

            # Check if the number of refused challenges in the past week is 0
            # also check for minimum number of challenges played = 5
            if not player.magic.has_modifier('ach-this-is-sparta'):
                if refused_challenges(player) == 0 and \
                                challenge_count(player, days=7) >= 5 and \
                                first_seen(player) >= 7:
                    cls.earn_achievement(player, 'ach-this-is-sparta')

            # Check if player played 10 challenges in a day"
            if not player.magic.has_modifier('ach-chall-10-a-day'):
                if challenges_played_today(player) >= 10:
                    cls.earn_achievement(player, 'ach-chall-10-a-day')

        if action == 'chall-won':
            # Check for flawless victory
            if get_chall_score(kwargs.get("arguments")) == 500:
                if not player.magic.has_modifier('ach-flawless-victory'):
                    cls.earn_achievement(player, 'ach-flawless-victory')
            # Check 10 won challenge games in a row
            if not player.magic.has_modifier('ach-chall-won-10'):
                if consecutive_chall_won(player) >= 10:
                    cls.earn_achievement(player, 'ach-chall-won-10')

            # Check if player defeated 2 levels or more bigger opponent
            if not player.magic.has_modifier('ach-chall-def-big'):
                if (kwargs.get('user_to').level_no - player.level_no) >= 2:
                    Activity.objects.create(timestamp=datetime.now(),
                                            user_from=player, user_to=player,
                                            action='defeat-better-player')
                    victories = Activity.objects.filter(user_to=player,
                                                        action='defeat-better-player')
                    if victories.count() >= 5:
                        cls.earn_achievement(player, 'ach-chall-def-big')
                        victories.delete()

            # Check if the player finished the challenge in less than 1 minute
            if not player.magic.has_modifier('ach-win-fast'):
                seconds_no = get_challenge_time(kwargs.get("arguments"))
                if seconds_no > 0 and seconds_no <= 60:
                    cls.earn_achievement(player, 'ach-win-fast')

        if action == 'message':
            # Check the number of unique users who send pm to player in the last m minutes
            if unique_users_pm(kwargs.get('user_to'), 15) >= 5:
                if not kwargs.get('user_to').magic.has_modifier('ach-popularity'):
                    cls.earn_achievement(kwargs.get('user_to'), 'ach-popularity')

        if action in ("login", "seen"):
            # Check login between 2-4 am
            if login_between_count(player, 3, 5) > 2:
                if not player.magic.has_modifier('ach-night-owl'):
                    cls.earn_achievement(player, 'ach-night-owl')
            if login_between_count(player, 6, 8) > 2:
                if not player.magic.has_modifier('ach-early-bird'):
                    cls.earn_achievement(player, 'ach-early-bird')

            if not player.magic.has_modifier('ach-god-mode-on'):
                if check_for_god_mode(player, 5, 5):
                    cls.earn_achievement(player, 'ach-god-mode-on')
            # Check previous 10 seens
            if consecutive_days_seen(player, datetime.now()) >= 14:
                if not player.magic.has_modifier('ach-login-10'):
                    cls.earn_achievement(player, 'ach-login-10')

        if action == 'cast':
            # Check if player is affected by 5 or more spells
            if not player.magic.has_modifier('ach-spell-5'):
                if spell_count(player) >= 5:
                    cls.earn_achievement(player, 'ach-spell-5')

            # Check if player used all non-mass spells
            if not player.magic.has_modifier('ach-use-all-spells'):
                if used_all_spells(player, False):
                    cls.earn_achievement(player, 'ach-use-all-spells')

            # Check if player used all mass spells
            if not player.magic.has_modifier('ach-use-all-mass'):
                if used_all_spells(player, True):
                    cls.earn_achievement(player, 'ach-use-all-mass')

        if 'buy' in action:
            # Check if player spent 500 gold on spells
            if not player.magic.has_modifier('ach-spent-gold'):
                if spent_gold(player) >= 500:
                    cls.earn_achievement(player, 'ach-spent-gold')

        if action == 'gold-won':
            # Check if player reached level 5
            if not player.magic.has_modifier('ach-level-5'):
                if player.level_no >= 5:
                    cls.earn_achievement(player, 'ach-level-5')
            # Check if player reached level 10
            if not player.magic.has_modifier('ach-level-10'):
                if player.level_no >= 10:
                    cls.earn_achievement(player, 'ach-level-10')

        if 'gold' in action:
            # Check if player has 300 gold
            if not player.magic.has_modifier('ach-gold-300'):
                if gold_amount(player) >= 300:
                    cls.earn_achievement(player, 'ach-gold-300')

        if 'login' in action:
            # Check if player got a head start login
            if not player.magic.has_modifier('ach-head-start'):
                # (player, start_hour, start_day, start_month, hour_offset)
                # server start date: hour, day, month
                # hour_offset = offset from start date when player will be rewarded
                if login_at_start(player, start_day=12, start_month=10):
                    cls.earn_achievement(player, 'ach-head-start')


    @classmethod
    def get_modifiers(self):
        return ['ach-login-10',
                'ach-qotd-10',
                'ach-chall-100',
                'ach-chall-won-10',
                'ach-chall-10-a-day',
                'ach-night-owl',
                'ach-early-bird',
                'ach-popularity',
                'ach-chall-def-big',
                'ach-this-is-sparta',
                'ach-flawless-victory',
                'ach-win-fast',
                'ach-god-mode-on',
                'ach-spell-5',
                'ach-level-5',
                'ach-level-10',
                'ach-gold-300',
                'ach-use-all-spells',
                'ach-use-all-mass',
                'ach-spent-gold',
                'ach-head-start',
        ]


def check_for_achievements(sender, **kwargs):
    Achievements.activity_handler(sender, **kwargs)


addActivity.connect(check_for_achievements)
messageSignal.connect(check_for_achievements)
