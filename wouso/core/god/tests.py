from django.contrib.auth.models import User, Group
import unittest
from . import get_god
from wouso.core.user.models import PlayerGroup
from wouso.games.challenge.models import ChallengeGame


__author__ = 'alex'


class GodTestCase(unittest.TestCase):

    def test_others_are_not_elligible_for_challenge(self):
        user, new = User.objects.get_or_create(username='33')
        game = ChallengeGame
        god = get_god()
        group, new = Group.objects.get_or_create(name="Others")
        others, new = PlayerGroup.objects.get_or_create(name="Others", group=group)
        player = user.get_profile()
        player.groups.add(others)
        self.assertFalse(god.user_is_eligible(player, game))


