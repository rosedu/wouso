from datetime import datetime, timedelta
from wouso.core.magic.models import Artifact
from wouso.core.tests import WousoTest
from wouso.interface.activity import signals
from wouso.games.qotd.models import QotdGame
from achievements import consecutive_seens
from achievements import consecutive_qotd_correct, unique_users_pm
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
        for i in range(10):
            timestamp=datetime.now() + timedelta(minutes = -1)
            a = Activity.objects.create(timestamp=timestamp, user_from=player,user_to=player, action='message', public=False)
        self.assertEqual(unique_users_pm(player,3),1)
    
    def popularity_test_5_pm_2(self):
        player = self._get_player()
        timestamp=datetime.now() + timedelta(minutes = -1)
        a = Activity.objects.create(timestamp=timestamp, user_from=player,user_to=player, action='message', public=False)
        a = Activity.objects.create(timestamp=timestamp, user_from=None,user_to=player, action='message', public=False)
        self.assertEqual(unique_users_pm(player,3),2)
    
    def popularity_test_5_pm_3(self):
        #Test for messages recieved from at least 1 user in the last 30 min
        player = self._get_player()
        Artifact.objects.create(group=Artifact.DEFAULT(), name='ach-popularity')
        timestamp = datetime.now() + timedelta(minutes=-1)
        a = Activity.objects.create(timestamp=timestamp, user_from=player,user_to=player, action='message', public=False)
        timestamp = datetime.now() + timedelta(minutes=-31)
        a = Activity.objects.create(timestamp=timestamp, user_from=None,user_to=player, action='message', public=False)
        activities = Activity.objects.filter(action='message',user_to=player,timestamp__gt=datetime.now()-timedelta(minutes=3))
        print activities
        signals.addActivity.send(sender=None, timestamp = timestamp,user_from=player,
                                     user_to=player,
                                     action='message',
                                     game=None)
        self.assertEqual(unique_users_pm(player,30),1)
        self.assertTrue(player.magic.has_modifier('ach-popularity'))

