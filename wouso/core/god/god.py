from wouso.core.artifacts.models import Artifact, Group
from wouso.core.game import get_games

class DefaultGod:
    """ A basic God implementation.
    This can be overriden by realm specific version of God. Every year, a new god must be written
    """

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
        if points < 80:
            return 1
        if points < 125:
            return 2
        if points < 180:
            return 3
        if points < 245:
            return 4
        if points < 320:
            return 5
        if points < 450:
            return 6
        return 7  # maximum level for now

    def get_all_modifiers(self):
        """ Fetch modifiers from games and also add specific ones
        """
        ms = []
        for g in get_games():
            ms.extend(g.get_modifiers())

        return ms