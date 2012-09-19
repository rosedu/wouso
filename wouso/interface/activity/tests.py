from datetime import datetime, timedelta
from wouso.core.magic.models import Artifact
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import ChallengeGame

from achievements import consecutive_seens, consecutive_chall_won, challenge_count
from models import Activity
from . import signals

class AchievementTest(WousoTest):

    def test_login_10(self):
        player = self._get_player()
        for i in range(10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.assertEqual(consecutive_seens(player, datetime.now()), 10)

    def test_login_10_wrong(self):
        player = self._get_player()
        for i in range(10):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                continue
            a = Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.assertEqual(consecutive_seens(player, datetime.now()), 5)

    def test_login_10_activity(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-login-10')
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.client.login(username=player.user.username, password='test')
        self.client.get('/hub/')

        self.assertTrue(player.magic.has_modifier('ach-login-10'))

    def test_chall_10_won(self):
        player = self._get_player()
        for i in range(1, 11):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
            message_string=str(i), public=True)

        self.assertEqual(consecutive_chall_won(player), 10)

    def test_chall_10_won_wrong_draw(self):
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                 a = Activity.objects.create(timestamp=timestamp,
                        user_from=player,user_to=player, action='chall-draw',
                        message_string=str(i), public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player,user_to=player, action='chall-won',
                        message_string=str(i), public=True)

        self.assertEqual(consecutive_chall_won(player), 4)

    def test_chall_10_won_wrong_lost(self):
        player1 = self._get_player()
        player2 = self._get_player(2)
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                 a = Activity.objects.create(timestamp=timestamp,
                        user_from=player2,user_to=player1, action='chall-won',
                        message_string=str(i), public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1,user_to=player2, action='chall-won',
                        message_string=str(i), public=True)

        self.assertEqual(consecutive_chall_won(player1), 4)

    def test_chall_10_won_activity(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-chall-won-10')
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=True)

        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='chall-won',
                                     game=ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-chall-won-10'))

    def test_chall_30(self):
        player = self._get_player()
        for i in range(1, 31):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=True)

        self.assertEqual(challenge_count(player), 30)

    def test_chall_30_draw_lost(self):
        player1 = self._get_player()
        player2 = self._get_player(2)
        for i in range(1, 31):
            timestamp = datetime.now() + timedelta(days=-i)
            if (i % 5) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player2,user_to=player1, action='chall-won',
                        message_string=str(i), public=True)
            elif (i % 7) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1,user_to=player2, action='chall-draw',
                        message_string=str(i), public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1,user_to=player2, action='chall-won',
                        message_string=str(i), public=True)

        self.assertEqual(challenge_count(player1), 30)

    def test_chall_30_activity(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-chall-30')
        player = self._get_player()
        for i in range(1, 30):
            timestamp = datetime.now() + timedelta(days=-i)
            if i % 5 == 0:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-draw',
                    message_string=str(i), public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=True)

        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='chall-won',
                                     game=ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-chall-30'))

