from wouso.core.magic.models import Artifact, Group, SpellHistory
from wouso.core.game import get_games
from django.contrib.auth.models import Group as DjangoGroup

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
        from wouso.core.scoring.models import Formula
        fs = []
        fs.append(Formula(id='buy-spell', formula='gold=-{price}',
            owner=None,
            description='Gold spent on spells')
        )
        fs.append(Formula(id='gold-points-rate', formula='points={gold}*3;gold=-{gold}',
            owner=None,
            description='Exchange gold in points')
        )
        fs.append(Formula(id='points-gold-rate', formula='points=-{points};gold={points}*0.1',
            owner=None,
            description='Exchange points in gold')
        )
        fs.append(Formula(id='bonus-gold', formula='gold={gold}', owner=None,
            description='Give bonus gold to the poor people'))
        fs.append(Formula(id='bonus-points', formula='points={points}', owner=None,
            description='Give bonus points'))
        fs.append(Formula(id='steal-points', formula='points={points}', owner=None,
            description='Steal points using spells'))
        fs.append(Formula(id='penalty-points', formula='points=-{points}', owner=None,
            description='Take back points from user'))
        return fs

    def get_user_level(self, level_no, player):
        """
        Return the artifact object for the given level_no.
        If there is a group for player series, use it.
        """
        try:
            group = Group.objects.get(name=player.series.name)
        except (Group.DoesNotExist, AttributeError):
            group = Artifact.DEFAULT()

        name = 'level-%d' % level_no
        try:
            artifact = Artifact.objects.get(name=name, group=group)
        except Artifact.DoesNotExist:
            try:
                artifact = Artifact.objects.get(name=name, group=Artifact.DEFAULT())
            except Artifact.DoesNotExist:
                return None

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
        ]
        for g in get_games():
            ms.extend(g.get_modifiers())

        return ms

    def get_artifact_for_modifier(self, modifier, player):
        """ Return the race-specific artifact object for given modifier """
        try:
            return Artifact.objects.get(group__name="Default", name=modifier)
        except Artifact.DoesNotExist:
            return None

    def can_cast(self, spell, source, destination):
        """ Check if destination can receive spell from source
        """
        source_play = source.race.can_play if source.race else False
        destin_play = destination.race.can_play if destination.race else False

        if source_play != destin_play:
            # This prevents Others from casting spells on actual players.
            return False

        if destination.has_modifier('immunity'):
            return False

        if destination.has_modifier('curse') and (spell.type != 'n'):
            return False

        if source.has_modifier('curse'):
            return False

        if (spell.name == 'steal') and (destination.points < spell.percents):
            return False

        if (spell.name == 'steal') and (source == destination):
            return False

        if spell.name == 'challenge-affect-scoring':
            existing = destination.spells.filter(spell__name='challenge-affect-scoring')
            if existing.count() > 0:
                # check if a spell with the same sign +/- exists
                for sp in existing:
                    if (sp.spell.percents * spell.percents) > 0:
                        return False
                # in order to apply this new spell, cancel existing, sign contrary, spells
                existing.delete()
        return True

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
        signals.addActivity.send(sender=None, user_from=psdue.source,
                                 user_to=psdue.player,
                                 message=signal_msg,
                                 arguments=dict(to=psdue.player),
                                 game=None)

        if psdue.spell.name == 'dispell':
            for psd in psdue.player.spells:
                psd.delete()
            return True
        if psdue.spell.name == 'cure':
            for psd in psdue.player.spells.filter(spell__type='n'):
                psd.delete()
            # also delete itself
            psdue.delete()
            return True
        if psdue.spell.name == 'steal':
            psdue.player.steal_points(psdue.source, psdue.spell.percents)
            psdue.delete()
            return True
        return False

    def user_is_eligible(self, player, game=None):
        if game is not None:
            game = str(game.__name__)

        if game == 'ChallengeGame':
            from wouso.core.user import models
            group, new = DjangoGroup.objects.get_or_create(name='Others')
            others, new = models.PlayerGroup.objects.get_or_create(name='Others', group=group)
            if others in player.groups.all():
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