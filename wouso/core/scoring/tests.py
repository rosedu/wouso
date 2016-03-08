from django.test import TestCase
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from wouso.core.config.models import IntegerListSetting
from wouso.core.game.models import Game
from wouso.core import scoring, signals
from wouso.core.tests import WousoTest
from wouso.core.user.models import Player
from models import Formula, Coin, History
from sm import FormulaParsingError, setup_scoring, CORE_POINTS, check_setup, update_points, calculate


class ScoringTestCase(TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='33')
        self.game = Game.get_instance()
        self.coin = Coin.add('_test')

    def tearDown(self):
        #self.user.delete()
        self.game.delete()
        self.coin.delete()

    def testHistoryFor(self):
        no_history = scoring.history_for(self.user, self.game, external_id=999)
        self.assertEqual(len(no_history), 0)

    def testScoreSimple(self):
        scoring.score_simple(self.user.get_profile(), self.coin, game=self.game, external_id=2, amount=10)
        multiple = scoring.history_for(self.user, self.game, external_id=2)

        self.assertTrue(isinstance(multiple, QuerySet))
        self.assertEqual(len(multiple), 1)

        history = list(multiple)[0]

        self.assertTrue(isinstance(history, History))
        self.assertEqual(history.amount, 10)

    def testCalculate(self):
        formula = Formula.add('_test_formula',
                              expression='_test=5', owner=self.game)

        # Call by name
        ret = scoring.calculate('_test_formula')
        self.assertTrue(isinstance(ret, dict))

        # Call by object
        ret = scoring.calculate(formula)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 5)

        formula2 = Formula.add('_test_formula2',
                               expression='_test=5*3', owner=self.game)

        ret = scoring.calculate(formula2)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 15)

        # Multiple coins
        formula2.expression = '_test=5*3; points=4'

        ret = scoring.calculate(formula2)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 15)
        self.assertEqual(ret['points'], 4)

        # Fail safe
        formula2.expression = '_test=5*cucu'
        try:
            ret = scoring.calculate(formula2)
            # no error? wtf
            self.assertFalse(True)
        except Exception as e:
            self.assertTrue(isinstance(e, FormulaParsingError))

    def testScore(self):
        formula = Formula.add('_test_formula_sc',
                              expression='_test=13', owner=self.game)

        scoring.score(self.user.get_profile(), self.game, formula,
                      external_id=3)

        hs = scoring.history_for(self.user, self.game, external_id=3)
        self.assertTrue(isinstance(hs, QuerySet))

        history = list(hs)[0]

        # check if specific coin has been updated
        self.assertEqual(history.coin, self.coin)
        self.assertEqual(history.amount, 13)


class UpdateScoringTest(WousoTest):
    def test_update_points_level_upgrade_first_time(self):
        level_up_points = 80
        IntegerListSetting.get('level_limits').set_value(str(level_up_points))
        Coin.add('points')
        Coin.add('gold')
        Formula.add('level-gold', expression='gold=10*{level}', owner=None)
        # Upgrade player's level
        player = self._get_player()
        player.points = level_up_points + 1
        player.level_no = 1
        player.save()
        update_points(player, None)
        coins = History.user_coins(player.user)
        self.assertEqual(coins['gold'], 10 * player.max_level)

    def test_update_points_level_downgrade(self):
        level_up_points = 80
        IntegerListSetting.get('level_limits').set_value(str(level_up_points))
        Coin.add('points')
        Coin.add('gold')
        Formula.add('level-gold', expression='gold=10*{level}', owner=None)
        # Upgrade player's level
        player = self._get_player()
        player.points = level_up_points + 1
        player.level_no = 1
        player.save()
        update_points(player, None)
        # Downgrade player's level
        player.points = level_up_points - 1
        player.save()
        update_points(player, None)
        coins = History.user_coins(player.user)
        self.assertEqual(coins['gold'], 10 * player.max_level)

    def test_update_points_level_upgrade_back(self):
        level_up_points = 80
        IntegerListSetting.get('level_limits').set_value(str(level_up_points))
        Coin.add('points')
        Coin.add('gold')
        Formula.add('level-gold', expression='gold=10*{level}', owner=None)
        # Upgrade player's level
        player = self._get_player()
        player.points = level_up_points + 1
        player.level_no = 1
        player.save()
        update_points(player, None)
        # Downgrade player's level
        player.points = level_up_points - 1
        player.save()
        update_points(player, None)
        #Upgrade player's level back
        player.points = level_up_points + 1
        player.save()
        update_points(player, None)
        coins = History.user_coins(player.user)
        self.assertEqual(coins['gold'], 10 * player.max_level)


class ScoringHistoryTest(WousoTest):
    def test_user_coins(self):
        Coin.add('points')
        Coin.add('gold')
        player = self._get_player()
        scoring.score_simple(player, 'points', 10)
        self.assertIn('points', History.user_coins(player.user))

    def test_user_points(self):
        coin = Coin.add('points')
        player = self._get_player()

        scoring.score_simple(player, 'points', 10)

        up = History.user_points(user=player.user)
        self.assertTrue('wouso' in up)
        self.assertTrue(coin.name in up['wouso'])
        self.assertEqual(up['wouso'][coin.name], 10)

    def test_accessors(self):
        player = self._get_player()
        self.assertEqual(scoring.user_coins(player), scoring.user_coins(player.user))

    def test_sync_methods(self):
        player = self._get_player()
        coin = Coin.add('points')

        History.objects.create(user=player.user, coin=coin, amount=10)
        self.assertEqual(player.points, 0)
        scoring.sync_user(player)
        self.assertEqual(player.points, 10)

        History.objects.create(user=player.user, coin=coin, amount=10)
        self.assertEqual(player.points, 10)
        scoring.sync_all_user_points()
        player = Player.objects.get(pk=player.pk)
        self.assertEqual(player.points, 20)


class ScoringSetupTest(TestCase):
    def test_check_setup(self):
        setup_scoring()
        self.assertTrue(check_setup())

    def test_setup(self):
        setup_scoring()
        for c in CORE_POINTS:
            self.assertTrue(Coin.get(c))


class ScoringFirstLogin(WousoTest):
    def test_first_login_points(self):
        f = Formula.add('start-points', expression='points=10')
        Coin.add('points')
        player = self._get_player()

        self.assertEqual(player.points, 0)

        # this won't work, since the activity is sent in our custom view
        #self.client.login(username=player.user.username, password='test')
        # using this instead
        signals.addActivity.send(sender=None, user_from=player, action="login", game=None, public=False)

        player = Player.objects.get(pk=player.pk)
        self.assertEqual(player.points, 10)


class ScoringTestFunctions(TestCase):
    def test_fibbonaci_formula(self):
        formula = Formula.add('test-fib', expression='points=fib(0)')
        value = calculate(formula)['points']

        self.assertEqual(value, 0)
        formula.expression = 'points=fib(1)'
        formula.save()
        value = calculate(formula)['points']

        self.assertEqual(value, 1)
        formula.expression = 'points=fib(2)'
        formula.save()
        value = calculate(formula)['points']

        self.assertEqual(value, 1)
        formula.expression = 'points=fib(3)'
        formula.save()
        value = calculate(formula)['points']

        self.assertEqual(value, 2)
        formula.expression = 'points=fib(4)'
        formula.save()
        value = calculate(formula)['points']

        self.assertEqual(value, 3)
