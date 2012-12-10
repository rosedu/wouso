from django.db.models import Q
from django.test import TestCase
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import Challenge
from models import GrandChallengeGame


class GrandChallengeTest(WousoTest):
    def test_start_gc(self):
        u1 = self._get_player(1)
        u2 = self._get_player(2)

        Challenge.LIMIT = 0
        Challenge.WARRANTY = False

        self.assertFalse(GrandChallengeGame.is_started())
        GrandChallengeGame.start()
        self.assertTrue(GrandChallengeGame.is_started())

        c = Challenge.objects.filter(Q(user_from__user=u1, user_to__user=u2)|Q(user_from__user=u2, user_to__user=u1))
        self.assertEqual(c.count(), 1)