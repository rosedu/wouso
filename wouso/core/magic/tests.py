import unittest
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from wouso.core import scoring
from wouso.core.magic.templatetags.artifacts import artifact, spell_due, artifact_full
from wouso.core.scoring.models import Coin, Formula
from wouso.core.tests import WousoTest
from wouso.core.user.models import Player
from models import *
from manager import MagicManager

class ManagerTestCase(WousoTest):
    """ Test the core.magic.manager.Manager helper.
    """
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.player = self.user.get_profile()

    def test_manager_properties(self):
        self.assertTrue(self.player.magic)

        self.assertIsInstance(self.player.magic, MagicManager)

        self.assertEqual(self.player.magic.spells.count(), 0)
        self.assertEqual(self.player.magic.spells_cast.count(), 0)
        self.assertEqual(self.player.magic.spells_available.count(), 0)
        self.assertEqual(self.player.magic.artifact_amounts.count(), 0)
        self.assertEqual(self.player.magic.spell_amounts.count(), 0)

        self.assertFalse(self.player.magic.has_modifier('inexistent-modifier'))
        self.assertEqual(self.player.magic.modifier_percents('inexistent-modifier'), 100) # should return 0

    def test_manager_use_modifier(self):
        Artifact.objects.create(name='modifier-name', group=Artifact.DEFAULT())
        self.player.magic.give_modifier('modifier-name', 1)
        self.assertTrue(self.player.magic.has_modifier('modifier-name'))

        self.player.magic.use_modifier('modifier-name', 1)
        self.assertFalse(self.player.magic.has_modifier('modifier-name'))

    def test_cast_spell(self):
        spell = Spell.objects.create(name='le-spell')

        player2 = self._get_player(2)
        self.player.magic.add_spell(spell)

        result = player2.magic.cast_spell(spell, self.player, datetime.now())

        self.assertFalse(result)

class ModifierTest(TestCase):
    def test_path_simple(self):
        m = Modifier(name='cici')
        self.assertTrue(m.path)
        self.assertEqual(m.path, 'cici')

    def test_path_image(self):
        m = Modifier(name='cici')
        m.image = 'test.jpg'
        self.assertTrue('test.jpg' in m.path)


class ArtifactTestCase(unittest.TestCase):

    def testArtifactCreateUnique(self):
        """ Test if we cannot create two artifacts with the same name in a group
        """
        group = ArtifactGroup.objects.create(name='gigi')

        a1 = Artifact.objects.create(group=group, name='name')

        self.assertRaises(IntegrityError, Artifact.objects.create, group=group, name='name')

    def test_no_artifact_behavior(self):
        noartifact = NoArtifactLevel(1)

        self.assertTrue(artifact(noartifact))

class SpellTestCase(WousoTest):

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

    def test_expired(self):
        player = self._get_player()
        spell = Spell.objects.create(name='test-spell', available=True, price=10)

        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=spell, due=datetime.now() + timedelta(days=1))
        self.assertFalse(PlayerSpellDue.get_expired(datetime.today()))

        obs.due = datetime.now() - timedelta(days=1)
        obs.save()

        self.assertTrue(PlayerSpellDue.get_expired(datetime.today()))
        self.assertIn(obs, PlayerSpellDue.get_expired(datetime.today()))

        obs.due = datetime.now() - timedelta(days=1)
        obs.save()

        # Run management task: should delete expired dues
        Bazaar.management_task()

        self.assertFalse(PlayerSpellDue.get_expired(datetime.today()))


class TemplatetagsTest(WousoTest):
    def test_spell_due(self):
        player = self._get_player()
        spell = Spell.objects.create(name='test-spell', available=True, price=10)

        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=spell, due=datetime.now() + timedelta(days=1))

        self.assertTrue(spell_due(obs))

    def test_artifact_full(self):
        self.assertFalse(artifact_full(None))

        player = self._get_player()
        self.assertTrue(artifact_full(player.level))