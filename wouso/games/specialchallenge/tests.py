from wouso.core.tests import WousoTest
from models import SpecialChallenge

class SpecialChallengeTest(WousoTest):
    def test_challenge_run(self):
        p1, p2 = self._get_player(1), self._get_player(2)
        c = SpecialChallenge.objects.create(player_from=p1, player_to=p2)
        c.launch()
        c.set_active()
        self.assertFalse(c.is_editable())
        c.update_challenge()
        self.assertTrue(c.real_challenge)
        c.real_challenge.accept()
        # fake play
        c.real_challenge.set_won_by_player(p1)
        # check status
        c = SpecialChallenge.objects.get(pk=c.pk) #refresh
        self.assertTrue(c.is_played())