import unittest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from wouso.core import scoring
from models import *
from wouso.core.scoring.models import Coin, Formula
from wouso.core.user.models import Player

class ArtifactTestCase(unittest.TestCase):

    def testArtifactCreateUnique(self):
        """ Test if we cannot create two artifacts with the same name in a group
        """
        group = ArtifactGroup.objects.create(name='gigi')

        a1 = Artifact.objects.create(group=group, name='name')

        self.assertRaises(IntegrityError, Artifact.objects.create, group=group, name='name')

class SpellTestCase(TestCase):

    def test_buy_spell(self):
        Coin.objects.create(id='gold')
        Formula.objects.create(id='buy-spell', formula="gold=-{price}")
        spell = Spell.objects.create(name='test-spell', available=True, price=10)
        player = User.objects.create_user('test', 'test@a.ro', password='test').get_profile()

        scoring.score_simple(player, 'gold', 100)
        self.assertEqual(player.coins['gold'], 100)

        # TODO: interface test should not be here
        response = self.client.get(reverse('bazaar_home'))
        self.assertTrue('test-spell' in response.content)

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('bazaar_buy', kwargs={'spell': spell.id}))
        self.assertFalse('error' in response.content)

        player = Player.objects.get(user__username='test')
        self.assertEqual(player.coins['gold'], 90)