from django.core.management import call_command
from django.test import TestCase
from models import Game


class TestGame(Game):
    class Meta:
        proxy = True


class TestGameModule(TestCase):
    def test_game_instance(self):
        gi = TestGame.get_instance()
        self.assertEqual(gi.name, 'TestGame')

        self.assertFalse(TestGame.get_formulas())
        self.assertFalse(TestGame.get_coins())
        self.assertFalse(TestGame.get_modifiers())
        self.assertFalse(gi.get_game_absolute_url())
        self.assertEqual(gi.__unicode__(), gi.name)
