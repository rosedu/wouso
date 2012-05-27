from django.contrib.auth.models import User, Group
from django.test import TestCase
from . import get_god
import unittest
from wouso.core.user.models import PlayerGroup
from wouso.games.challenge.models import ChallengeGame


__author__ = 'alex'


class GodTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testgod')
        self.player = self.user.get_profile()

    def test_others_are_not_elligible_for_challenge(self):
        god = get_god()
        others, new = PlayerGroup.objects.get_or_create(name="Others")

        self.player.groups.add(others)
        self.assertFalse(god.user_is_eligible(self.player, ChallengeGame))

    def test_users_are_elligible_for_challenge(self):
        god = get_god()
        self.assertTrue(god.user_is_eligible(self.player, ChallengeGame))


    def test_user_can_interact_with_users(self):
        user2 = User.objects.create(username='testgod2')
        player2 = user2.get_profile()

        god = get_god()

        self.assertTrue(god.user_can_interact_with(self.player, player2))


    @unittest.expectedFailure
    def test_user_can_interact_with_others(self):
        user2 = User.objects.create(username='testgod2')
        player2 = user2.get_profile()
        others, new = PlayerGroup.objects.get_or_create(name="Others")
        player2.groups.add(others)

        god = get_god()

        self.assertFalse(god.user_can_interact_with(self.player, player2))

