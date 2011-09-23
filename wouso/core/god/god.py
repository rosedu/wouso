from wouso.core.magic.models import Artifact, Group
from wouso.core.game import get_games

class DefaultGod:
    """ A basic God implementation and also the base class for other gods.
    It defines the game basics, such as level intervals and species.
    This can be overriden by realm specific version of God. Every year,
    a new god can/must be written.
    """
    LEVEL_LIMITS = (80, 125, 180, 245, 320, 450)

    def get_user_level(self, level_no, player=None):
        """
        Return the artifact object for the given level_no.
        """
        group, new =  Group.objects.get_or_create(name='Default')
        name = 'level-%d' % level_no
        try:
            artifact = Artifact.objects.get(name=name, group=group)
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
            current_limit = DefaultGod.LEVEL_LIMITS[level_no - 2]
        except:
            current_limit = 0
        try:
            next_limit = DefaultGod.LEVEL_LIMITS[level_no - 1]
        except:
            next_limit = 1000

        return dict(next_level=level_no + 1, points_gained=points-current_limit, points_left=next_limit-points)

    def get_all_modifiers(self):
        """ Fetch modifiers from games and also add specific ones
        """
        ms = []
        for g in get_games():
            ms.extend(g.get_modifiers())

        return ms

    def get_artifact_for_modifier(self, modifier, player):
        """ Return the race-specific artifact object for given modifier """
        try:
            return Artifact.objects.get(group__name="Default", name=modifier)
        except Artifact.DoesNotExist:
            return None
