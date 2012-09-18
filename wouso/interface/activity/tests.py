from datetime import datetime, timedelta
from wouso.core.magic.models import Artifact
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import ChallengeGame

from achievements import consecutive_seens, consecutive_chall_won, challenge_count
from models import Activity

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
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=true)

        self.assertEqual(consecutive_chall_won(player), 10)

    def test_chall_10_won_wrong(self):
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=true)

        self.assertEqual(consecutive_chall_won(player), 5)

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
        for i in range(1, 30):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=true)

        self.assertEqual(challenge_count(player), 30)

    def test_chall_30_wrong(self):
        player = self._get_player()
        for i in range(1, 30):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=true)

        self.assertEqual(challenge_count(player), 25)

    def test_chall_30_activity(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-chall-30')
        player = self._get_player()
        for i in range(1, 30):
            timestamp = datetime.now() + timedelta(days=-i)
            if mod(i, 5) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-draw',
                    message_string=str(i), public=true)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player,user_to=player, action='chall-won',
                    message_string=str(i), public=true)

        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='chall-won',
                                     game=ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-chall-30'))

