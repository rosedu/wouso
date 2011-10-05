import unittest
from wouso.core.magic.models import Artifact
from django.contrib.auth.models import User

class PlayerTestCase(unittest.TestCase):
    def testModifierPercents(self):
        artif = Artifact.objects.create(name='test', group=Artifact.DEFAULT(), percents=50)
        user = User.objects.create(username='-pt-test')
        player = user.get_profile()

        player.give_modifier('test', 1)
        self.assertEqual(player.modifier_percents('test'), 150)

        player.give_modifier('test', 1)
        self.assertEqual(player.modifier_percents('test'), 200)

        artif.percents = -50
        artif.save()
        self.assertEqual(player.modifier_percents('test'), 0)

        user.delete()
        artif.delete()