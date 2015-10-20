import unittest

from django.db.models import Q
from django.test import TestCase
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import Challenge
from models import GrandChallengeGame, GrandChallenge, GrandChallengeUser


class GrandChallengeTest(WousoTest):
    def setUp(self):
        Challenge.LIMIT = 0
        Challenge.WARRANTY = False
        super(GrandChallengeTest, self).setUp()

    def test_start_gc(self):
        u1 = self._get_player(1)
        u2 = self._get_player(2)

        GrandChallengeGame.reset()
        self.assertFalse(GrandChallengeGame.is_started())
        GrandChallengeGame.start()
        self.assertTrue(GrandChallengeGame.is_started())

        c = Challenge.objects.filter(Q(user_from__user=u1, user_to__user=u2)|Q(user_from__user=u2, user_to__user=u1))
        self.assertEqual(c.count(), 1)

    def _simulate_n_users(self, n):
        """
        Create n users and simulate a GC run.
        """
        for i in range(n):
            self._get_player(i)

        GrandChallengeGame.start()
        self.assertEqual(GrandChallengeGame.get_current_round().round_number, 1)
        self.assertEqual(GrandChallengeGame.base_query().count(), n)
        self.assertEqual(len(GrandChallengeGame.get_current_round().participants()), n - n % 2)
        while not GrandChallengeGame.is_finished():
            GrandChallengeGame.round_next()
        GrandChallengeGame.force_round_close(GrandChallengeGame.get_current_round())
        GrandChallengeGame.round_next()
        GrandChallengeGame.force_round_close(GrandChallengeGame.get_current_round())

    # TODO: Fix the following tests that have been written based on a broken set_won_by_player()
    # method found in games/challenge/models.py.
    @unittest.skip
    def test_4_players(self):
        self._simulate_n_users(4)
        self.assertEqual(GrandChallengeGame.get_winner().id, self._get_player(1).id)

    @unittest.skip
    def test_5_players(self):
        self._simulate_n_users(5)
        self.assertEqual(GrandChallengeGame.get_winner().id, self._get_player(1).id)

    @unittest.skip
    def test_6_players(self):
        self._simulate_n_users(6)
        self.assertEqual(GrandChallengeGame.get_winner().id, self._get_player(1).id)

    @unittest.skip
    def test_16_players(self):
        self._simulate_n_users(16)
        self.assertEqual(GrandChallengeGame.get_winner().id, self._get_player(1).id)

    @unittest.skip
    def test_16_players(self):
        self._simulate_n_users(17)
        self.assertEqual(GrandChallengeGame.get_winner().id, self._get_player(1).id)

class GCUserTest(WousoTest):
    def setUp(self):
        Challenge.LIMIT = 0
        Challenge.WARRANTY = False
        super(GCUserTest, self).setUp()

    def test_get_challenges_active_and_played(self):
        u1 = self._get_player(1)
        u2 = self._get_player(2)

        Challenge.SCORING = False

        gc1 = u1.get_extension(GrandChallengeUser)
        gc2 = u2.get_extension(GrandChallengeUser)
        self.assertFalse(gc1.get_challenges())
        chall = GrandChallenge.create(u1, u2, round=3)
        self.assertEqual(gc1.get_challenges().count(), 1)
        self.assertEqual(gc2.get_challenges().count(), 1)
        self.assertEqual(gc1.get_active().count(), 1)
        chall.challenge.set_won_by_player(u1)
        self.assertEqual(gc1.get_active().count(), 0)
        self.assertEqual(gc2.get_active().count(), 0)
        self.assertEqual(gc1.get_played().count(), 1)
        self.assertEqual(gc2.get_played().count(), 1)