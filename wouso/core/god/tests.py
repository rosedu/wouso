import unittest
from django.contrib.auth.models import User
from django.test import TestCase
from wouso.core.config.models import IntegerListSetting
from wouso.core.magic.models import NoArtifactLevel
from wouso.core.user.models import PlayerGroup, Race
from wouso.games.challenge.models import ChallengeGame
from . import get_god


class GodTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testgod')
        self.player = self.user.get_profile()

    def test_get_systems_formulas(self):
        god = get_god()

        sf = god.get_system_formulas()
        self.assertTrue(sf)

    def test_user_level(self):
        god = get_god()

        level = god.get_user_level(self.player.level_no, self.player)
        self.assertIsInstance(level, NoArtifactLevel)

    def test_get_level_limit(self):
        IntegerListSetting.get('level_limits').set_value("80 125 180 245 320 450")
        god = get_god()

        self.assertEqual(god.get_level_for_points(0), 1)
        self.assertNotEqual(god.get_level_for_points(10000), 1)

    def test_get_player_progress(self):
        god = get_god()

        progress = god.get_level_progress(self.player)
        self.assertEqual(progress['next_level'], self.player.level_no + 1)

    def test_get_all_modifiers(self):
        god = get_god()

        self.assertTrue('dispell' in god.get_all_modifiers())

    def test_get_artifact(self):
        god = get_god()

        self.assertFalse(god.get_artifact_for_modifier('inexistant-modifier', self.player))

    def test_unaffiliated_are_not_elligible_for_challenge(self):
        god = get_god()
        unaffiliated_race, new = Race.objects.get_or_create(name="Unaffiliated", can_play=False)

        self.player.race = unaffiliated_race
        self.player.save()
        self.assertFalse(god.user_is_eligible(self.player, ChallengeGame))

    def test_users_are_elligible_for_challenge(self):
        god = get_god()
        race = Race.objects.get_or_create(name='-race', can_play=True)[0]
        self.player.race = race
        self.player.save()
        self.assertTrue(god.user_is_eligible(self.player, ChallengeGame))

    def test_user_can_interact_with_users(self):
        user2 = User.objects.create(username='testgod2')
        player2 = user2.get_profile()

        god = get_god()

        self.assertTrue(god.user_can_interact_with(self.player, player2))

    @unittest.expectedFailure
    def test_user_can_interact_with_unaffiliated(self):
        user2 = User.objects.create(username='testgod2')
        player2 = user2.get_profile()
        unaffiliated, new = PlayerGroup.objects.get_or_create(name="Unaffiliated", can_play=False)
        unaffiliated.players.add(player2)

        god = get_god()

        self.assertFalse(god.user_can_interact_with(self.player, player2))
