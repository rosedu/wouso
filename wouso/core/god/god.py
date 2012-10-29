from wouso.core.magic.models import Artifact, ArtifactGroup, SpellHistory, NoArtifactLevel
from wouso.core.game import get_games

class DefaultGod:
    """ A basic God implementation and also the base class for other gods.
    It defines the game basics, such as level intervals and species.
    This can be overriden by realm specific version of God. Every year,
    a new god can/must be written.
    """
    LEVEL_LIMITS = (80, 125, 180, 245, 320, 450)

    def get_system_formulas(self):
        """ Return formulas used by the meta wouso game.
        If inherited, should not override super's result, but extend it.
        """
        fs = [
            dict(id='start-points', formula='points=420', owner=None,
                description='Points received at the start of the game'),
            dict(id='buy-spell', formula='gold=-{price}', owner=None,
                description='Gold spent on spells'),
            dict(id='gold-points-rate', formula='points={gold}*3;gold=-{gold}', owner=None,
                description='Exchange gold in points'),
            dict(id='points-gold-rate', formula='points=-{points};gold={points}*0.1', owner=None,
                description='Exchange points in gold'),
            dict(id='bonus-gold', formula='gold={gold}', owner=None,
                description='Give bonus gold to the poor people'),
            dict(id='bonus-points', formula='points={points}', owner=None,
                description='Give bonus points'),
            dict(id='steal-points', formula='points={points}', owner=None,
                description='Steal points using spells'),
            dict(id='penalty-points', formula='points=-{points}', owner=None,
                description='Take back points from user'),
            dict(id='level-gold', formula='gold=10*{level}', owner=None,
                description='Bonus gold on level upgrade'),
            dict(id='general-infraction', formula='penalty=10', owner=None,
                description='Give penalty points to suspicious users'),
            dict(id='chall-was-set-up-infraction', formula='penalty=20', owner=None,
                description='Give penalty points for losing a challenge on purpose')
        ]
        return fs

    def get_user_level(self, level_no, player):
        """
        Return the artifact object for the given level_no.
        If there is a group for player series, use it.
        """
        try:
            group = ArtifactGroup.objects.get(name=player.race.name)
        except (ArtifactGroup.DoesNotExist, AttributeError):
            group = Artifact.DEFAULT()

        name = 'level-%d' % level_no
        try:
            artifact = Artifact.objects.get(name=name, group=group)
        except Artifact.DoesNotExist:
            try:
                artifact = Artifact.objects.get(name=name, group=Artifact.DEFAULT())
            except Artifact.DoesNotExist:
                return NoArtifactLevel(level_no)

        return artifact

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
        for i, limit in enumerate(DefaultGod.LEVEL_LIMITS):
            if points < limit:
                return i + 1
        return 7  # maximum level for now

    def get_level_progress(self, player):
        """ Get player progress inside its level """
        level_no = player.level_no
        points = player.points
        try:
            if level_no == 1:
                current_limit = 0
            else:
                current_limit = DefaultGod.LEVEL_LIMITS[level_no - 2]
        except:
            current_limit = 0
        try:
            next_limit = DefaultGod.LEVEL_LIMITS[level_no - 1]
        except:
            next_limit = 1000

        points_gained = points - current_limit
        if next_limit > current_limit:
            percent = round(100.0 * points_gained / (next_limit - current_limit))
        else:
            percent = round(100.0 * points_gained / next_limit)

        return dict(next_level=level_no + 1, points_gained=points_gained , points_left=next_limit-points, percent=percent)

    def get_all_modifiers(self):
        """ Fetch modifiers from games and also add system specific ones
        """
        ms = ['dispell', # cancel all spells
              'cure',   # delete all negative spells
              'curse',  # prevent cast of positive spells, or cure and dispell
              'immunity', # prevent cast of any spells, or cure and dispell
              'steal',  # allow users to steal points, one from another
              'top-disguise', # allow showing another number of points in top
        ]
        for g in get_games():
            ms.extend(g.get_modifiers())

        from wouso.interface import get_apps
        for a in get_apps():
            ms.extend(a.get_modifiers())

        return ms

    def get_artifact_for_modifier(self, modifier, player):
        """ Return the race-specific artifact object for given modifier """
        try:
            return Artifact.objects.get(group__name="Default", name=modifier)
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

        if destination.has_modifier('immunity'):
            return False, 'Player has immunity'

        if destination.has_modifier(spell.name):
                return False, 'Player already has this spell casted on him'


        if destination.has_modifier('curse') and (spell.type != 'n'):
            return False, 'Player is cursed'

        if source.has_modifier('curse'):
            return False, 'Player is cursed'

        if (spell.name == 'steal') and (destination.points < spell.percents):
            return False, 'Insufficient amount'

        if (spell.name == 'steal') and (source == destination):
            return False, 'Cannot steal from self'

        if spell.name == 'challenge-affect-scoring':
           if spell_cleanup(spell, destination, spell.name) == False:
               return False, 'Something wrong'
        if spell.name == 'challenge-affect-scoring-won':
            if spell_cleanup(spell, destination, spell.name) == False:
                return False, 'Something wrong'
        return True, None

    def post_cast(self, psdue):
        """ Execute action after a spell is cast. This is used to implement specific spells
        such as 'clean any existing spell' cast.

        Returns True if action has been taken, False if not.
        """
        # Always executed, so log
        SpellHistory.used(psdue.source, psdue.spell, psdue.player)
        # Also trigger anonymous activiy
        from wouso.interface.activity import signals
        if psdue.source == psdue.player:
            signal_msg = 'a facut o vraja asupra sa.'
        else:
            signal_msg = 'a facut o vraja asupra {to}.'
        action_msg = 'cast'
        signals.addActivity.send(sender=None, user_from=psdue.source,
                                 user_to=psdue.player,
                                 message=signal_msg,
                                 arguments=dict(to=psdue.player),
                                 action=action_msg,
                                 game=None)

        if psdue.spell.name == 'dispell':
            for psd in psdue.player.magic.spells:
                self.post_expire(psd)
                psd.delete()
            return True
        if psdue.spell.name == 'cure':
            for psd in psdue.player.magic.spells.filter(spell__type='n'):
                self.post_expire(psd)
                psd.delete()
            # also delete itself
            psdue.delete()
            return True
        if psdue.spell.name == 'steal':
            psdue.player.steal_points(psdue.source, psdue.spell.percents)
            psdue.delete()
            return True

        if psdue.spell.name == 'top-disguise':
            psdue.player.points = 1.0 * psdue.player.points * psdue.player.magic.modifier_percents('top-disguise') / 100
            psdue.player.save()
        return False

    def post_expire(self, psdue):
        """
         Execute an action right before a spell expires
        """
        from wouso.core import scoring
        if psdue.spell.name == 'top-disguise':
            psdue.player.points = scoring.real_points(psdue.player)
            psdue.player.save()

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
                position_diff = abs(player_from.get_extension(TopUser).position - player_to.get_extension(TopUser).position)
                rule = ceil(position_diff * 0.1)
                if rule > 7:
                    rule = 7 # nu bloca mai mult de 7 zile
                if rule <= elapsed_days:
                    return True
                return False

        return True
        

def spell_cleanup(spell,destination,spell_name):
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
