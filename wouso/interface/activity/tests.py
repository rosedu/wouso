from datetime import datetime, timedelta
from wouso.core.magic.models import Artifact, Spell, SpellHistory
from wouso.core.magic.manager import MagicManager
from wouso.core.tests import WousoTest
from wouso.core import scoring, signals
from wouso.core.scoring.models import Coin
from wouso.games.qotd.models import QotdGame
from wouso.games.challenge.models import ChallengeGame, ChallengeUser, Challenge
from wouso.interface.apps.messaging.models import Message, MessagingUser
from achievements import consecutive_days_seen, consecutive_qotd_correct, consecutive_chall_won, challenge_count, \
                refused_challenges, get_challenge_time, unique_users_pm, wrong_first_qotd, get_chall_score, \
                challenges_played_today, check_for_god_mode, spell_count, spent_gold, gold_amount, \
                Achievements
from models import Activity

class AchievementTest(WousoTest):
    def test_login_with_multiple_seens(self):
        """
        Multiple seens every day for more than 14 days in a row.
        """
        player = self._get_player()
        for i in range(100):
            timestamp = datetime.now() - timedelta(hours=i*16)
            Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)
        self.assertGreaterEqual(consecutive_days_seen(player, datetime.now()), 14)

    def test_login_10(self):
        """
        One seen every day for 14 days in a row.
        """
        player = self._get_player()
        for i in range(14):
            timestamp = datetime.now() + timedelta(days=-i)
            Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.assertEqual(consecutive_days_seen(player, datetime.now()), 14)


    def test_login_10_less(self):
        """
        Multiple seens every day for less than 14 days in a row.
        """

        player = self._get_player()
        for i in range(20):
            timestamp = datetime.now() - timedelta(hours=i*7)
            Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)
        self.assertLess(consecutive_days_seen(player, datetime.now()), 14)


    def test_login_10_wrong(self):
        player = self._get_player()
        for i in range(14):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                continue
            Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.assertEqual(consecutive_days_seen(player, datetime.now()), 5)

    def test_login_10_activity(self):
        Artifact.objects.create(group=None, name='ach-login-10')
        player = self._get_player()
        for i in range(1, 14):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, action='seen', public=False)

        self.client.login(username=player.user.username, password='test')
        self.client.get('/hub/')

        self.assertTrue(player.magic.has_modifier('ach-login-10'))

    def test_early_bird_not(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-early-bird')
        for i in range(1,2):
            Activity.objects.create(timestamp=datetime(2012,9,17,6,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        for i in range(1,4):
            Activity.objects.create(timestamp=datetime(2012,9,17,5,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        signals.addActivity.send(sender=None, timestamp=datetime(2012,9,17,5,0,0),
            user_from=player,
            user_to=player,
            action='seen',
            game=None)
        self.assertFalse(player.magic.has_modifier('ach-early-bird'))

    def test_early_bird_set(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-early-bird')
        for i in range(1,4):
            Activity.objects.create(timestamp=datetime(2012,9,17,6,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        signals.addActivity.send(sender=None, timestamp=datetime(2012,9,17,6,0,0),
            user_from=player,
            user_to=player,
            action='seen',
            game=None)
        self.assertTrue(player.magic.has_modifier('ach-early-bird'))

    def test_night_owl_not(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-night-owl')
        for i in range(1,3):
            Activity.objects.create(timestamp=datetime(2012,9,17,6,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        for i in range(1,4):
            Activity.objects.create(timestamp=datetime(2012,9,17,5,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        signals.addActivity.send(sender=None, timestamp=datetime(2012,9,17,4,0,0),
                user_from=player,
                user_to=player,
                action='seen',
                game=None)
        self.assertFalse(player.magic.has_modifier('ach-night-owl'))

    def test_night_owl_set(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-night-owl')
        for i in range(1,4):
            Activity.objects.create(timestamp=datetime(2012,9,17,4,0,0),
                    user_from=player, user_to=player, action='seen', public=False)

        signals.addActivity.send(sender=None, timestamp=datetime(2012,9,17,4,0,0),
                user_from=player,
                user_to=player,
                action='seen',
                game=None)
        self.assertTrue(player.magic.has_modifier('ach-night-owl'))


class QotdAchievementTest(WousoTest):
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
        Artifact.objects.create(group=None, name='ach-qotd-10')
        player = self._get_player()
        for i in range(10):
            timestamp=datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct',message_string=str(i),public=True)
        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='qotd-correct',
                                     game=QotdGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-qotd-10'))


class ChallengeAchievementTest(WousoTest):
    def test_chall_10_won(self):
        player = self._get_player()
        for i in range(1, 11):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player, user_to=player, action='chall-won',
                    public=True)

        self.assertEqual(consecutive_chall_won(player), 10)

    def test_chall_10_won_wrong_draw(self):
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                 a = Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player, action='chall-draw',
                        public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player, action='chall-won',
                        public=True)

        self.assertEqual(consecutive_chall_won(player), 4)

    def test_chall_10_won_wrong_lost(self):
        player1 = self._get_player()
        player2 = self._get_player(2)
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            if i == 5:
                 a = Activity.objects.create(timestamp=timestamp,
                        user_from=player2, user_to=player1, action='chall-won',
                        public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1, user_to=player2, action='chall-won',
                        public=True)

        self.assertEqual(consecutive_chall_won(player1), 4)

    def test_chall_10_won_activity(self):
        Artifact.objects.create(group=None, name='ach-chall-won-10')
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                    user_from=player, user_to=player, action='chall-won',
                    public=True)

        self.assertFalse(player.magic.has_modifier('ach-chall-won-10'))
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
                    user_from=player, user_to=player, action='chall-won',
                    public=True)

        self.assertEqual(challenge_count(player), 30)

    def test_chall_100_draw_lost(self):
        player1 = self._get_player()
        player2 = self._get_player(2)
        for i in range(1, 101):
            timestamp = datetime.now() + timedelta(days=-i)
            if (i % 5) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player2, user_to=player1, action='chall-won',
                        public=True)
            elif (i % 7) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1, user_to=player2, action='chall-draw',
                        public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                        user_from=player1, user_to=player2, action='chall-won',
                        public=True)

        self.assertEqual(challenge_count(player1), 100)

    def test_chall_100_activity(self):
        Artifact.objects.create(group=None, name='ach-chall-100')
        player = self._get_player()
        for i in range(1, 100):
            timestamp = datetime.now() + timedelta(days=-i)
            if i % 5 == 0:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player, user_to=player, action='chall-draw',
                    public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                    user_from=player, user_to=player, action='chall-won',
                    public=True)

        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='chall-won',
                                     game=ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-chall-100'))

    def test_defeated_better_player_activity(self):
        Artifact.objects.create(group=None, name='ach-chall-def-big')
        player1 = self._get_player()
        player2 = self._get_player(2)
        player2.level_no = 4
        player2.save()

        for i in range(1,5):
            signals.addActivity.send(sender=None, user_from=player1,
                                        user_to=player2,
                                        action='chall-won',
                                        game=ChallengeGame.get_instance())
            self.assertFalse(player1.magic.has_modifier('ach-chall-def-big'))

        signals.addActivity.send(sender=None, user_from=player1,
                                    user_to=player2,
                                    action='chall-won',
                                    game=ChallengeGame.get_instance())
        self.assertTrue(player1.magic.has_modifier('ach-chall-def-big'))

    def test_this_is_sparta_correct(self):
        player = self._get_player()
        for i in range(1, 7):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                user_from=player, user_to=player, action='chall-refused',
                public=True)

        self.assertEqual(refused_challenges(player), 6)

    def test_this_is_sparta_activity_not_given(self):
        Artifact.objects.create(group=None, name='ach-this-is-sparta')
        player1 = self._get_player()
        player2 = self._get_player(2)
        first_seen = datetime.now() + timedelta(days=-10)#10 days since first login
        Activity.objects.create(timestamp=first_seen,
                user_from=player1, user_to=player1, action='seen',
                public=False)
        for i in range(1, 7):
            timestamp = datetime.now() + timedelta(days=-i)
            if (i % 4) == 0:
                a = Activity.objects.create(timestamp=timestamp,
                user_from=player1, user_to=player2, action='chall-refused',
                public=True)
            else:
                a = Activity.objects.create(timestamp=timestamp,
                user_from=player1, user_to=player2, action='chall-lost',
                public=True)
        #send signal to enable achievement validation
        signals.addActivity.send(sender=None, user_from=player1,
                                    user_to=player2,
                                    action='chall-refused',
                                    game=ChallengeGame.get_instance())
        #False due to refused challenge
        self.assertFalse(player1.magic.has_modifier('ach-this-is-sparta'))

    def test_this_is_sparta_activity_not_enough_challenges(self):
        Artifact.objects.create(group=None, name='ach-this-is-sparta')
        player1 = self._get_player()
        player2 = self._get_player(2)
        first_seen = datetime.now() + timedelta(days=-10)#10 days since first login
        Activity.objects.create(timestamp=first_seen,
                user_from=player1, user_to=player1, action='seen',
                public=False)
        for i in range(1, 3):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                user_from=player1, user_to=player2, action='chall-lost',
                public=True)
        #send signal to enable achievement validation
        signals.addActivity.send(sender=None, user_from=player1,
                                    user_to=player2,
                                    action='chall-won',
                                    game=ChallengeGame.get_instance())
        #False due to not enough challenges played
        self.assertFalse(player1.magic.has_modifier('ach-this-is-sparta'))

    def test_this_is_sparta_activity_not_enough_time(self):
        Artifact.objects.create(group=None, name='ach-this-is-sparta')
        player1 = self._get_player()
        player2 = self._get_player(2)
        first_seen = datetime.now() + timedelta(days=-6)#only 6 days have passed
        Activity.objects.create(timestamp=first_seen,
                user_from=player1, user_to=player1, action='seen',
                public=False)
        for i in range(1, 5):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                user_from=player1, user_to=player2, action='chall-lost',
                public=True)
        #send signal to enable achievement validation
        signals.addActivity.send(sender=None, user_from=player1,
                                    user_to=player2,
                                    action='chall-won',
                                    game=ChallengeGame.get_instance())
        #achievement condition earned
        self.assertFalse(player1.magic.has_modifier('ach-this-is-sparta'))

    def test_this_is_sparta_activity_passed(self):
        Artifact.objects.create(group=None, name='ach-this-is-sparta')
        player1 = self._get_player()
        player2 = self._get_player(2)
        first_seen = datetime.now() + timedelta(days=-7)#barely enough time
        Activity.objects.create(timestamp=first_seen,
                user_from=player1, user_to=player1, action='seen',
                public=False)
        for i in range(1, 5):
            timestamp = datetime.now() + timedelta(days=-i)
            a = Activity.objects.create(timestamp=timestamp,
                user_from=player1, user_to=player2, action='chall-lost',
                public=True)
        #send signal to enable achievement validation
        signals.addActivity.send(sender=None, user_from=player1,
                                    user_to=player2,
                                    action='chall-won',
                                    game=ChallengeGame.get_instance())
        #achievement condition earned
        self.assertTrue(player1.magic.has_modifier('ach-this-is-sparta'))

    def test_challenges_played_today(self):
        player = self._get_player()
        for i in range(1, 10):
            timestamp = datetime.now()
            if (i % 4) == 0:
                Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player,
                        action="chall-lost", public=True)
            else:
                Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player,
                        action="chall-won", public=True)
        self.assertEqual(challenges_played_today(player), 9)

    def test_challenges_played_today_activity(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-chall-10-a-day')
        for i in range(1, 10):
            timestamp = datetime.now()
            if (i % 4) == 0:
                Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player,
                        action="chall-lost", public=True)
            else:
                Activity.objects.create(timestamp=timestamp,
                        user_from=player, user_to=player,
                        action="chall-won", public=True)

        signals.addActivity.send(sender=None, user_from=player,
                                    user_to=player,
                                    action='chall-won',
                                    game=ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-chall-10-a-day'))

class PopularityTest(WousoTest):
    def setUp(self):
        Message.disable_check()

    def tearDown(self):
        Message.enable_check()

    def test_popularity_5_pm_1(self):
        player = self._get_player()
        player = player.get_extension(MessagingUser)
        for i in range(10):
            timestamp=datetime.now() + timedelta(minutes = -1)
            a = Message.objects.create(timestamp=timestamp, sender=player,receiver=player,subject = "a",text = "b")
        self.assertEqual(unique_users_pm(player,3),1)

    def test_popularity_5_pm_2(self):
        player = self._get_player()
        player=player.get_extension(MessagingUser)
        timestamp=datetime.now() + timedelta(minutes = -1)
        a = Message.objects.create(timestamp=timestamp, sender=player,receiver=player,subject = "a",text = "b")
        a = Message.objects.create(timestamp=timestamp, sender=self._get_player(2).get_extension(MessagingUser),receiver=player,subject = "a",text = "b")
        self.assertEqual(unique_users_pm(player,3),2)

    def test_popularity_5_pm_3(self):
        Artifact.objects.create(group=None, name='ach-popularity')
        user_to = self._get_player(100).get_extension(MessagingUser)
        for i in range(10):
            player = self._get_player(i).get_extension(MessagingUser)
            if i <= 3:
                timestamp = datetime.now() + timedelta(minutes=-10)
                a = Message.objects.create(timestamp=timestamp, sender=player,receiver=user_to,subject = "a",text = "b")
            else:
                timestamp = datetime.now() + timedelta(minutes=-35)
                a = Message.objects.create(timestamp=timestamp, sender=player,receiver=user_to,subject = "a",text = "b")
        Message.send(sender=player,receiver=user_to,subject="a",text="b")

        self.assertEqual(unique_users_pm(user_to,30),5)
        self.assertTrue(user_to.magic.has_modifier('ach-popularity'))


class NotificationsTest(WousoTest):
    def test_ach_notification(self):
        player = self._get_player()
        Artifact.objects.create(group=None, name='ach-notfication')
        Achievements.earn_achievement(player, 'ach-notfication')
        self.assertEqual(len(Message.objects.all()), 1)


class FlawlessVictoryTest(WousoTest):
    def setUp(self):
        super(FlawlessVictoryTest, self).setUp()
        self.user_from = self._get_player(1)
        self.user_to   = self._get_player(2)
        self.chall_user1 = self.user_from.get_extension(ChallengeUser)
        self.chall_user2 = self.user_to.get_extension(ChallengeUser)
        scoring.setup_scoring()
        self.chall = Challenge.create(user_from=self.chall_user1, user_to=self.chall_user2, ignore_questions=True)


    def test_scorring(self):
        self.chall.user_from.score = 100
        self.chall.user_from.save()
        self.chall.user_to.score = 200
        self.chall.user_to.save()
        self.assertEqual(get_chall_score(dict(id=self.chall.id)),200)
        self.chall.user_from.score = 300
        self.chall.user_from.save()
        self.assertEqual(get_chall_score(dict(id=self.chall.id)),300)
        self.chall.user_to.score = 500
        self.chall.user_to.save()
        self.assertEqual(get_chall_score(dict(id=self.chall.id)),500)

    def test_ach_fake(self):
        Artifact.objects.create(group=None, name='ach-flawless-victory')
        player=self._get_player()
        self.chall.user_from.score = 100
        self.chall.user_from.save()
        self.chall.user_to.score = 200
        self.chall.user_to.save()
        signals.addActivity.send(sender=None, user_from=player, user_to=player, arguments=dict(id=self.chall.id), action="chall-won", game=None)
        self.assertTrue(not player.magic.has_modifier('ach-flawless-victory'))
        self.chall.user_from.score = 500
        self.chall.user_from.save()
        signals.addActivity.send(sender=None, user_from=player, user_to=player, arguments=dict(id=self.chall.id), action="chall-won", game=None)
        self.assertTrue(player.magic.has_modifier('ach-flawless-victory'))

    def test_ach_real(self):
        Artifact.objects.create(group=None, name='ach-flawless-victory')
        self.chall.user_from.score = 500
        self.chall.user_from.save()
        self.chall.user_to.score = 200
        self.chall.user_to.save()

        self.assertFalse(self.user_from.magic.has_modifier('ach-flawless-victory'))
        self.chall.played()
        self.assertTrue(self.user_from.magic.has_modifier('ach-flawless-victory'))

class WinFastTest(WousoTest):
    def setUp(self):
        super(WinFastTest, self).setUp()
        user_from = self._get_player(1)
        user_to = self._get_player(2)
        chall_user1 = user_from.get_extension(ChallengeUser)
        chall_user2 = user_to.get_extension(ChallengeUser)
        scoring.setup_scoring()
        self.chall = Challenge.create(user_from=chall_user1, user_to=chall_user2, ignore_questions=True)

    def test_get_time(self):
        self.chall.user_from.seconds_took = 30
        self.chall.user_from.score = 500
        self.chall.user_from.save()
        self.chall.user_to.seconds_took = 80
        self.chall.user_to.score = 0
        self.chall.user_to.save()
        self.chall.winner = self.chall.user_from.user
        self.chall.save()
        self.assertEqual(get_challenge_time(dict(id=self.chall.id)), 30)

        self.chall.user_from.seconds_took = 180
        self.chall.user_from.save()
        self.chall.user_to.seconds_took = 20
        self.chall.user_to.save()

        self.assertEqual(get_challenge_time(dict(id=self.chall.id)), 180)

    def test_ach(self):
        Artifact.objects.create(group=None, name='ach-win-fast')
        player = self._get_player()
        self.chall.user_from.seconds_took = 30
        self.chall.user_from.score = 400
        self.chall.user_from.save()
        self.chall.user_to.seconds_took = 80
        self.chall.user_to.score = 300
        self.chall.user_to.save()
        self.chall.winner = self.chall.user_from.user
        self.chall.save()

        signals.addActivity.send(sender=None, user_from=player,
                                 user_to=player,
                                 arguments=dict(id=self.chall.id),
                                 action="chall-won",
                                 game = ChallengeGame.get_instance())
        self.assertTrue(player.magic.has_modifier('ach-win-fast'))


class SpellAchievement(WousoTest):

    def test_spell_count(self):
        player = self._get_player()
        spell = Spell.objects.create(name="test", title="", description="",
                image=None, percents=100, type='s')
        player.magic.add_spell(spell)
        player.magic.cast_spell(spell, player, datetime.now() + timedelta(days=3))
        self.assertTrue(player.magic.is_spelled)
        self.assertTrue(spell_count(player), 1)


    def test_spell_count_activity(self):
        Artifact.objects.create(group=None, name='ach-spell-5')
        player = self._get_player()
        for i in range(1, 6):
            name = "test" + str(i)
            spell = Spell.objects.create(name=name, title="", description="",
                    image=None, percents=100)
            player.magic.add_spell(spell)
            player.magic.cast_spell(spell, player, datetime.now() + timedelta(days=i))
        signals.addActivity.send(sender=None, user_from=player,
                user_to=player, action="cast", game=None)
        self.assertTrue(player.magic.has_modifier('ach-spell-5'))

    def test_gold_spent(self):
        player = self._get_player()
        spell = Spell.objects.create(name="test", title="", description="",
                                    image=None, percents=100, type='s',
                                    price=25)
        SpellHistory.objects.create(type='b', user_from=player, user_to=player,
                                date=datetime.now(), spell=spell)
        self.assertTrue(spent_gold(player), 25)

    def test_gold_spent_activity(self):
        Artifact.objects.create(group=None, name='ach-spent-gold')
        player = self._get_player()
        spell = Spell.objects.create(name="test", title="", description="",
                                    image=None, percents=100, type='s',
                                    price=600)
        SpellHistory.objects.create(type='b', user_from=player, user_to=player,
                                date=datetime.now(), spell=spell)
        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='spell-buy',
                                game=None)

        self.assertTrue(player.magic.has_modifier('ach-spent-gold'))

    def test_used_all_spells_activity(self):
        Artifact.objects.create(group=None, name='ach-use-all-spells')
        player = self._get_player()
        spell = Spell.objects.create(name="test", title="", description="",
                                    image=None, percents=100, type='s',
                                    price=600)
        SpellHistory.objects.create(type='u', user_from=player, user_to=player,
                                date=datetime.now(), spell=spell)
        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='cast',
                                game=None)

        self.assertTrue(player.magic.has_modifier('ach-use-all-spells'))

    def test_used_all_mass_spells_activity(self):
        Artifact.objects.create(group=None, name='ach-use-all-mass')
        player = self._get_player()
        spell = Spell.objects.create(name="test", title="", description="",
                                    image=None, percents=100, type='s',
                                    price=600, mass=True)
        SpellHistory.objects.create(type='u', user_from=player, user_to=player,
                                date=datetime.now(), spell=spell)
        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='cast',
                                game=None)

        self.assertTrue(player.magic.has_modifier('ach-use-all-mass'))


class LevelUpTest(WousoTest):

    def test_level_ach(self):
        Artifact.objects.create(group=None, name='ach-level-5')
        Artifact.objects.create(group=None, name='ach-level-10')
        coin = Coin.add('gold')
        player = self._get_player()
        player.level_no = 5
        player.save()

        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='gold-won',
                                game=None)
        self.assertTrue(player.magic.has_modifier('ach-level-5'))

        player.level_no = 10
        player.save()

        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='gold-won',
                                game=None)
        self.assertTrue(player.magic.has_modifier('ach-level-10'))


class GoldTest(WousoTest):

    def test_gold_amount(self):
        player = self._get_player()
        coin = Coin.add('gold')

        scoring.score_simple(player, coin, amount=100)

        self.assertEqual(gold_amount(player), 100)

    def test_gold_amount_ach(self):
        Artifact.objects.create(group=None, name='ach-gold-300')
        player = self._get_player()
        coin = Coin.add('gold')

        scoring.score_simple(player, coin, amount=500)

        signals.addActivity.send(sender=None, user_from=player,
                                user_to=player, action='gold-won',
                                game=None)
        self.assertTrue(player.magic.has_modifier('ach-gold-300'))


class GodModeTest(WousoTest):

    def test_check_for_god_mode1(self):
        player=self._get_player()
        timestamp=datetime.now()
        for i in range(5):
            timestamp -= timedelta(days=1)
            Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct')
        self.assertTrue(check_for_god_mode(player,5,0))

    def test_check_for_god_mode2(self):
        player=self._get_player()
        timestamp=datetime.now()
        for i in range(5):
            timestamp -= timedelta(days=1)
            if i == 3:
                Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-wrong')
                continue
            Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct')
        self.assertFalse(check_for_god_mode(player,5,0))

    def test_check_for_god_mode3(self):
        player = self._get_player()
        player2 = self._get_player(1)
        timestamp = datetime.now()
        for i in range(5):
            timestamp -= timedelta(days=1)
            Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player2, action='chall-won')
            Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='qotd-correct')
        self.assertTrue(check_for_god_mode(player,5,5))

        Artifact.objects.create(group=None, name='ach-god-mode-on')
        signals.addActivity.send(sender=None, user_from=player,
                                     user_to=player,
                                     action='seen',
                                     game=None)
        self.assertTrue(player.magic.has_modifier('ach-god-mode-on'))


    def test_check_for_god_mode4(self):
        player = self._get_player()
        player2 = self._get_player(1)
        timestamp = datetime.now()
        for i in range(5):
            timestamp -= timedelta(days=1)
            Activity.objects.create(timestamp=timestamp, user_from=player, user_to=player, action='chall-correct')
            if i == 3:
                Activity.objects.create(timestamp=timestamp, user_from=player2, user_to=player, action='chall-won')
                continue
        self.assertFalse(check_for_god_mode(player,5,0))
