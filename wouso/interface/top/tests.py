from wouso.core.tests import WousoTest
from wouso.interface.top.models import TopUser

class TopTest(WousoTest):
    def test_challenges(self):
        player = self._get_player()
        top_player = player.get_extension(TopUser)

        self.assertEqual(top_player.won_challenges, 0)