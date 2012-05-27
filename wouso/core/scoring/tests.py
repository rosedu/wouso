import unittest
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from wouso.core.game.models import Game
from wouso.core.scoring.models import Formula, Coin, History
from wouso.core.scoring import FormulaParsingError
from wouso.core import scoring

class ScoringTestCase(unittest.TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='33')
        self.game = Game.get_instance()
        self.coin = Coin.objects.create(id='_test')

    def tearDown(self):
        #self.user.delete()
        self.game.delete()
        self.coin.delete()

    def testHistoryFor(self):
        no_history = scoring.history_for(self.user, self.game, external_id=999)
        self.assertEqual(len(no_history), 0 )

    def testScoreSimple(self):
        scoring.score_simple(self.user.get_profile(), self.coin, game=self.game, external_id=2, amount=10)
        multiple = scoring.history_for(self.user, self.game, external_id=2)

        self.assertTrue(isinstance(multiple, QuerySet))
        self.assertEqual(len(multiple), 1)

        history = list(multiple)[0]

        self.assertTrue(isinstance(history, History))
        self.assertEqual(history.amount, 10)

    def testCalculate(self):
        formula = Formula.objects.create(id='_test_formula',
            formula='_test=5', owner=self.game)

        # Call by name
        ret = scoring.calculate('_test_formula')
        self.assertTrue(isinstance(ret, dict))

        # Call by objcet
        ret = scoring.calculate(formula)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 5)

        formula2 = Formula.objects.create(id='_test_formula2',
            formula='_test=5*3', owner=self.game)

        ret = scoring.calculate(formula2)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 15)

        # Multiple coins
        formula2.formula='_test=5*3; points=4'

        ret = scoring.calculate(formula2)
        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(ret['_test'], 15)
        self.assertEqual(ret['points'], 4)

        # Fail safe
        formula2.formula='_test=5*cucu'
        try:
            ret = scoring.calculate(formula2)
            # no error? wtf
            self.assertFalse(true)
        except Exception as e:
            self.assertTrue(isinstance(e, FormulaParsingError))

    def testScore(self):
        formula = Formula.objects.create(id='_test_formula_sc',
            formula='_test=13', owner=self.game)

        scoring.score(self.user.get_profile(), self.game, formula,
            external_id=3)

        hs = scoring.history_for(self.user, self.game, external_id=3)
        self.assertTrue(isinstance(hs, QuerySet))

        history = list(hs)[0]

        # check if specific coin has been updated
        self.assertEqual(history.coin, self.coin)
        self.assertEqual(history.amount, 13)
