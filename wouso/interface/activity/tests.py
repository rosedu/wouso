from datetime import datetime, timedelta
from wouso.core.magic.models import Artifact
from wouso.core.tests import WousoTest
from wouso.interface.activity import signals
from wouso.games.qotd.models import QotdGame
from achievements import consecutive_seens
from achievements import consecutive_qotd_correct, unique_users_pm ,wrong_first_qotd
from models import Activity
from wouso.interface.apps.messaging.models import Message,MessagingUser
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
        
    def test_10_qotd_3ok(self):
        player = self._get_player()
        for i in range(3):
            timestamp=datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct',message_string=str(i),public=True)
        self.assertEqual(consecutive_qotd_correct(player),3)
    
    def test_10_qotd_1wrong(self):
        player = self._get_player()
        for i in range(10):
            timestamp=datetime.now() - timedelta(days=-i)
            if i == 5:
                a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-wrong',message_string=str(i),public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct',message_string=str(i),public=True)
        self.assertEqual(consecutive_qotd_correct(player),4)
    
    def test_10_qotd_get_ach(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-qotd-10')
        player = self._get_player()
        for i in range(10):
            timestamp=datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct',message_string=str(i),public=True)
        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='qotd-correct',
                                     game=QotdGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-qotd-10'))
        
    def test_early_bird_not(self):
        player = self._get_player()
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-early-bird')
        signals.addActivity.send(sender=None, timestamp = datetime(2012,9,17,5,0,0),user_from=player,
                                     user_to=player,
                                     action='login',
                                     game=None)
        self.assertTrue(not player.magic.has_modifier('ach-early-bird'))
        
    def test_early_bird_set(self):
        player = self._get_player()
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-early-bird')
        signals.addActivity.send(sender=None, timestamp = datetime(2012,9,17,6,0,0),user_from=player,
                                     user_to=player,
                                     action='login',
                                     game=None)
        self.assertTrue(player.magic.has_modifier('ach-early-bird'))
        
    def test_night_owl_not(self):
        player = self._get_player()
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-night-owl')
        signals.addActivity.send(sender=None, timestamp = datetime(2012,9,17,4,0,0),user_from=player,
                                     user_to=player,
                                     action='login',
                                     game=None)
        self.assertTrue(not player.magic.has_modifier('ach-night-owl'))
        
    def test_night_owl_set(self):
        player = self._get_player()
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-night-owl')
        signals.addActivity.send(sender=None, timestamp = datetime(2012,9,17,3,0,0),user_from=player,
                                     user_to=player,
                                     action='login',
                                     game=None)
        self.assertTrue(player.magic.has_modifier('ach-night-owl'))
        
    def popularity_test_5_pm_1(self):
        player = self._get_player()
        player = player.get_extension(MessagingUser)
        for i in range(10):
            timestamp=datetime.now() + timedelta(minutes = -1)
            a = Message.objects.create(timestamp=timestamp, sender=player,receiver=player,subject = "a",text = "b")
        self.assertEqual(unique_users_pm(player,3),1)
    
    def popularity_test_5_pm_2(self):
        player = self._get_player()
        player=player.get_extension(MessagingUser)
        timestamp=datetime.now() + timedelta(minutes = -1)
        a = Message.objects.create(timestamp=timestamp, sender=player,receiver=player,subject = "a",text = "b")
        a = Message.objects.create(timestamp=timestamp, sender=self._get_player(2).get_extension(MessagingUser),receiver=player,subject = "a",text = "b")
        self.assertEqual(unique_users_pm(player,3),2)
    
    def popularity_test_5_pm_3(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-popularity')
        user_to = self._get_player(100).get_extension(MessagingUser)
        for i in range(10):
            player = self._get_player(i).get_extension(MessagingUser)
            if i <= 3:
                timestamp = datetime.now() + timedelta(minutes=-1)
                a = Message.objects.create(timestamp=timestamp, sender=player,receiver=user_to,subject = "a",text = "b")
            else:
                timestamp = datetime.now() + timedelta(minutes=-35)
                a = Message.objects.create(timestamp=timestamp, sender=player,receiver=user_to,subject = "a",text = "b")
        Message.send(sender=player,receiver=user_to,subject="a",text="b")
        
        self.assertEqual(unique_users_pm(user_to,30),5)
        self.assertTrue(user_to.magic.has_modifier('ach-popularity'))
    def bad_start_1(self):
        player = self._get_player()
        a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-wrong',message_string=str(i),public=True)
        self.assertTrue(wrong_first_qotd(player))
        a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-wrong',message_string=str(i),public=True)
        self.assertTrue(not wrong_first_qotd(player))
    def bad_start_2(self):
        player = self._get_player()
        a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct',message_string=str(i),public=True)
        self.assertTrue(not wrong_first_qotd(player))
        a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-wrong',message_string=str(i),public=True)
        self.assertTrue(not wrong_first_qotd(player))
    def bad_start_3(self):
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-bad-start')
        player = self._get_player()
        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='qotd-wrong',
                                     game=QotdGame.get_instance())
        self.assertTrue(user_to.magic.has_modifier('ach-bad-start'))
