from django.utils.translation import ugettext as _
from wouso.core import signals
from wouso.core.magic.models import Artifact, ArtifactGroup, SpellHistory, NoArtifactLevel
from wouso.core.game import get_games
from wouso.core.config.models import IntegerListSetting


class DefaultGod:
    """ A basic God implementation and also the base class for other gods.
    It defines the game basics, such as level intervals and species.
    This can be overriden by realm specific version of God. Every year,
    a new god can/must be written.
    """

    def get_level_limits(self):
        return IntegerListSetting.get('level_limits').get_value()

    def get_system_formulas(self):
        """ Return formulas used by the meta wouso game.
        If inherited, should not override super's result, but extend it.
        """
        fs = [
            dict(name='start-points', expression='points=420', owner=None,
                 description='Points received at the start of the game'),
            dict(name='buy-spell', expression='gold=-{price}', owner=None,
                 description='Gold spent on spells'),
            dict(name='gold-points-rate', expression='points={gold}*3;gold=-{gold}', owner=None,
                 description='Exchange gold in points'),
            dict(name='points-gold-rate', expression='points=-{points};gold={points}*0.1', owner=None,
                 description='Exchange points in gold'),
            dict(name='bonus-gold', expression='gold={gold}', owner=None,
                 description='Give bonus gold to the poor people'),
            dict(name='bonus-points', expression='points={points}', owner=None,
                 description='Give bonus points'),
            dict(name='penalty-points', expression='points=-{points}', owner=None,
                 description='Take back points from user'),
            dict(name='level-gold', expression='gold=10*{level}', owner=None,
                 description='Bonus gold on level upgrade'),
            dict(name='general-infraction', expression='penalty=10', owner=None,
                 description='Give penalty points to suspicious users'),
            dict(name='chall-was-set-up-infraction', expression='penalty=20', owner=None,
                 description='Give penalty points for losing a challenge on purpose'),
            dict(name='head-start', expression='points=200', owner=None,
                 description='Points earned for logging in the head start period'),
            dict(name='bonus-karma', expression='gold={karma_points}*10', owner=None,
                 description='Bonus given for earning Karma Points'),
        ]
        return fs

    def get_race_level(self, level_no, race):
        if isinstance(race, unicode):
            group = ArtifactGroup.get(race)
        elif race:
            group = ArtifactGroup.get(race.name)
        else:
            group = None

        name = 'level-%d' % level_no
        full_name = '%s-%s-%s' % (group.name if group else 'default', name, 100)
        full_fallback = '%s-%s-%s' % ('default', name, 100)
        return Artifact.get(full_name) or Artifact.get(full_fallback) or NoArtifactLevel(level_no)

    def get_user_level(self, level_no, player):
        """
        Return the artifact object for the given level_no.
        If there is a group for player series, use it.
        """
        return self.get_race_level(level_no, player.race_name)

    def get_level_for_points(self, points, player=None):
        """ Implement points limits, for passing a level points must be in an interval.
        For example (v3):
            nivelul 1: 0 - 80p
            nivelul 2: 80p - 125p
            nivelul 3: 125 - 180p
            nivelul 4: 180 - 245p
            nivelul 5: 245 - 320p
            nivelul 6: 320 - 450p
            nivelul 7: 450 -
        """
        level_limits = self.get_level_limits()
        for i, limit in enumerate(level_limits):
            if points < limit:
                return i + 1
        return 1 + len(level_limits)  # maximum level

    def get_level_progress(self, player):
        """ Get player progress inside its level """
        level_no = player.level_no
        points = player.points
        level_limits = self.get_level_limits()
        try:
            if level_no == 1:
                current_limit = 0
            else:
                current_limit = level_limits[level_no - 2]
        except:
            current_limit = 0
        try:
            next_limit = level_limits[level_no - 1]
        except:
            next_limit = 1000

        points_gained = points - current_limit
        if next_limit > current_limit:
            percent = round(100.0 * points_gained / (next_limit - current_limit))
        else:
            percent = round(100.0 * points_gained / next_limit)

        return dict(next_level=level_no + 1, points_gained=points_gained, points_left=next_limit - points,
                    percent=percent)

    def get_all_modifiers(self):
        """ Fetch modifiers from games and also add system specific ones
        """
        ms = ['dispell',  # cancel all spells
              'cure',  # delete all negative spells
              'curse',  # prevent cast of positive spells, or cure and dispell
              'immunity',  # prevent cast of any spells, or cure and dispell
              'top-disguise',  # allow showing another number of points in top
            ]

        for g in get_games():
            ms.extend(g.get_modifiers())

        from wouso.interface.apps import get_apps

        for a in get_apps():
            ms.extend(a.get_modifiers())

        return ms

    def get_artifact_for_modifier(self, modifier, player):
        """ Return the race-specific artifact object for given modifier """
        try:
            return Artifact.objects.get(name=modifier)
        except Artifact.DoesNotExist:
            return None

    def can_cast(self, spell, source, destination):
        """ Check if destination can receive spell from source

        Return: a tuple of (can_cast, error_message)
        """
        source_play = source.race.can_play if source.race else False
        destin_play = destination.race.can_play if destination.race else False

        if source_play != destin_play:
            # This prevents Others from casting spells on actual players.
            return False, 'Different world races'

        if (spell.type == 'p') and (source.race != destination.race):
            return False, 'Different race player'

        if (spell.type == 'n') and (source.race == destination.race):
            return False, 'Player is the same race as you'

        if destination.magic.has_modifier('immunity'):
            return False, 'Player has immunity'

        if destination.magic.has_modifier(spell.name):
            return False, 'Player already has this spell cast on him'

        if destination.magic.has_modifier('curse') and (spell.type != 'n'):
            return False, 'Player is cursed'

        if source.magic.has_modifier('curse'):
            return False, 'Player is cursed'

        if spell.name == 'challenge-affect-scoring':
            if not spell_cleanup(spell, destination, spell.name):
                return False, 'Something wrong'
        if spell.name == 'challenge-affect-scoring-won':
            if not spell_cleanup(spell, destination, spell.name):
                return False, 'Something wrong'
        return True, None

    def user_is_eligible(self, player, game=None):
        if game is not None:
            game = str(game.__name__)

        if game == 'ChallengeGame':
            if not player.race or not player.race.can_play:
                return False

        return True

    def user_can_interact_with(self, player_from, player_to, game=None):
        if game is not None:
            game = str(game.__name__)

        if game == 'ChallengeGame':
            from datetime import datetime
            from math import ceil
            from wouso.interface.top.models import TopUser
            from wouso.games.challenge.models import Challenge

            lastch = Challenge.last_between(player_from, player_to)
            if lastch:
                elapsed_days = (datetime.now() - lastch.date).days
                position_diff = abs(
                    player_from.get_extension(TopUser).position - player_to.get_extension(TopUser).position)
                rule = ceil(position_diff * 0.1)
                if rule > 7:
                    rule = 7  # nu bloca mai mult de 7 zile
                if rule <= elapsed_days:
                    return True
                return False

        return True


def spell_cleanup(spell, destination, spell_name):
    """
    This function eliminates same type spells with contrary sign +/-
    """
    existing = destination.magic.spells.filter(spell__name=spell_name)
    if existing.count() > 0:
        # check if a spell with the same sign +/- exists
        for sp in existing:
            if (sp.spell.percents * spell.percents) > 0:
                return False
    # in order to apply this new spell, cancel existing, sign contrary, spells
    existing.delete()
    return True


# Define the receivers for postCast and postExpire signals
def post_cast(sender, **kwargs):
    """ Execute action after a spell is cast. This is used to implement specific spells
    such as 'clean any existing spell' cast.

    Returns True if action has been taken, False if not.
    """

    try:
        psdue = kwargs['psdue']
    except:
        return

    # Log usage to SpellHistory
    SpellHistory.used(psdue.source, psdue.spell, psdue.player)
    # Special actions
    if psdue.spell.name == 'dispell':
        for psd in psdue.player.magic.spells:
            signals.postExpire.send(sender=None, psdue=psd)
            psd.delete()
        return True

    if psdue.spell.name == 'cure':
        for psd in psdue.player.magic.spells.filter(spell__type='n'):
            signals.postExpire.send(sender=None, psdue=psd)
            psd.delete()
        # also delete itself
        psdue.delete()
        return True

    if psdue.spell.name == 'top-disguise':
        psdue.player.points = 1.0 * psdue.player.points * psdue.player.magic.modifier_percents('top-disguise') / 100
        psdue.player.save()
    return False


def post_expire(sender, **kwargs):
    """
     Execute an action right before a spell expires
    """

    try:
        psdue = kwargs['psdue']
    except:
        return

    from wouso.core import scoring

    if psdue.spell.name == 'top-disguise':
        psdue.player.points = scoring.real_points(psdue.player)
        psdue.player.save()


signals.postCast.connect(post_cast)
signals.postExpire.connect(post_expire)
