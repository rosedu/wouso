from django.db.models import Q
from django.test import TestCase
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import Challenge
from models import GrandChallengeGame, GrandChallenge, GrandChallengeUser


class GrandChallengeTest(WousoTest):
    def setUp(self):
        Challenge.LIMIT = 0
        Challenge.WARRANTY = False

    def test_start_gc(self):
        u1 = self._get_player(1)
        u2 = self._get_player(2)


        self.assertFalse(GrandChallengeGame.is_started())
        GrandChallengeGame.start()
        self.assertTrue(GrandChallengeGame.is_started())

        c = Challenge.objects.filter(Q(user_from__user=u1, user_to__user=u2)|Q(user_from__user=u2, user_to__user=u1))
        self.assertEqual(c.count(), 1)


class GCUserTest(WousoTest):
    def setUp(self):
        Challenge.LIMIT = 0
        Challenge.WARRANTY = False

    def test_get_challenges_active_and_played(self):
        u1 = self._get_player(1)
        u2 = self._get_player(2)

        Challenge.SCORING = False

        gc1 = u1.get_extension(GrandChallengeUser)
        gc2 = u2.get_extension(GrandChallengeUser)
        self.assertFalse(gc1.challenges())
        chall = GrandChallenge.create(u1, u2, round=3)
        self.assertEqual(gc1.challenges().count(), 1)
        self.assertEqual(gc2.challenges().count(), 1)
        self.assertEqual(gc1.get_active().count(), 1)
        chall.challenge.set_won_by_player(u1)
        self.assertEqual(gc1.get_active().count(), 0)
        self.assertEqual(gc2.get_active().count(), 0)
        self.assertEqual(gc1.get_played().count(), 1)
        self.assertEqual(gc2.get_played().count(), 1)
