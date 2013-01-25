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
        Artifact.objects.create(name='modifier-name')
        self.player.magic.give_modifier('modifier-name', 1)
        self.assertTrue(self.player.magic.has_modifier('modifier-name'))

        self.player.magic.use_modifier('modifier-name', 1)
        self.assertFalse(self.player.magic.has_modifier('modifier-name'))

    def test_cast_spell(self):
        spell1 = Spell.objects.create(name='le-spell')
        spell2 = Spell.objects.create(name='le-spell2', mass=True, type='o')
        v = []
        for i in range(0,7):
            player = self._get_player(i+2)
            player.points = 10-i
            player.save()
            v.append(player)

        v[3].magic.add_spell(spell2)
        neigh = v[3].get_neighbours_from_top(2)
        neigh = v[3].magic.filter_players_by_spell(neigh, spell2)
        v[3].magic.mass_cast(spell2, neigh, datetime.now()+timedelta(days=1))

        for i in [1, 2, 4, 5]:
            self.assertTrue(v[i].magic.is_spelled)
        self.assertTrue(v[3].magic.is_spelled)

        v[6].magic.cast_spell(spell1, v[0], datetime.now()+timedelta(days=1))
        self.assertFalse(v[6].magic.is_spelled)

        v[0].magic.add_spell(spell1)
        v[6].magic.cast_spell(spell1, v[0], datetime.now()+timedelta(days=1))
        self.assertTrue(v[6].magic.is_spelled)


class ModifierTest(TestCase):
    def test_path_simple(self):
        m = Modifier(name='cici')
        self.assertTrue(m.path)
        self.assertEqual(m.path, 'cici')

    def test_path_image(self):
        m = Modifier(name='cici')
        m.image = 'test.jpg'
        self.assertTrue('test.jpg' in m.path)


class ArtifactTestCase(TestCase):

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
        Coin.add('gold')
        Formula.add('buy-spell', definition="gold=-{price}")
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

    def test_cure(self):
        """
         Test if cure works on a player
        """
        player = self._get_player()
        player2 = self._get_player(2)

        spell = Spell.objects.create(name='test-spell', available=True, price=10, type='n')
        cure = Spell.objects.create(name='cure', available=True, price=10)
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=spell, due=datetime.now() + timedelta(days=1))

        self.assertTrue(player.magic.spells) # There is test-spell cast on myself

        player2.magic.add_spell(cure)
        player.magic.cast_spell(cure, player2, datetime.now() + timedelta(days=1))

        self.assertFalse(player.magic.spells) # There isn't any spell left

    def test_disguise_simple(self):
        """
         Test if top-disguise spell works
        """
        player = self._get_player()
        Coin.add('points')
        scoring.score_simple(player, 'points', 10)

        self.assertEqual(player.points, 10)

        disguise = Spell.objects.create(name='top-disguise', available=True, price=10, percents=50, type='s')
        player.magic.add_spell(disguise)
        player.magic.cast_spell(disguise, player, datetime.now() + timedelta(days=1))

        self.assertTrue(player.magic.has_modifier('top-disguise'))

        self.assertEqual(player.points, 15)

    def test_disguise_expire_on_dispell(self):
        player = self._get_player()
        Coin.add('points')
        scoring.score_simple(player, 'points', 10)

        disguise = Spell.objects.create(name='top-disguise', available=True, price=10, percents=50, type='s')
        player.magic.add_spell(disguise)
        player.magic.cast_spell(disguise, player, datetime.now() + timedelta(days=1))

        self.assertEqual(player.points, 15)

        dispell = Spell.objects.create(name='dispell', available=True, price=10)
        player.magic.add_spell(dispell)
        player.magic.cast_spell(dispell, player)

        self.assertFalse(player.magic.has_modifier('top-disguise'))

        player = Player.objects.get(pk=player.pk)

        self.assertEqual(player.points, 10)


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
