import unittest
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase
from django.test.client import Client
from django.utils.translation import ugettext as _
from wouso.core import scoring
from wouso.core.magic.templatetags.artifacts import artifact, spell_due, artifact_full
from wouso.core.scoring.models import Coin, Formula
from wouso.core.tests import WousoTest
from wouso.core.user.models import Player
from wouso.core.magic.models import Spell
from wouso.games.challenge.models import Challenge, ChallengeUser, ChallengeGame
from wouso.games.qotd.models import QotdUser
from wouso.games.qotd.tests import _make_question_for_today
from wouso.interface.activity.models import Activity
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
        self.assertEqual(self.player.magic.modifier_percents('inexistent-modifier'), 100)  # should return 0

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
        for i in range(0, 7):
            player = self._get_player(i + 2)
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

    def test_dispell(self):
        """
         Test if dispell works on a player
        """
        player = self._get_player()

        pos_spell = Spell.objects.create(name='positive-test-spell', available=True, price=10, type='p')
        neg_spell = Spell.objects.create(name='negative-test-spell', available=True, price=10, type='n')
        dispell = Spell.objects.create(name='dispell', available=True, price=20, type='o')

        player.magic.add_spell(dispell)

        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=pos_spell, due=datetime.now() + timedelta(days=1))
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=neg_spell, due=datetime.now() + timedelta(days=1))
        self.assertTrue(player.magic.spells)  # Check if there is an active spell on player

        player.magic.cast_spell(dispell, player, datetime.now())
        self.assertFalse(player.magic.spells)  # No spells should be active on player after dispell

    def test_dispell_no_due(self):
        """
         Dispell should not remain active on player after cast
        """
        player = self._get_player()

        dispell = Spell.objects.create(name='dispell', available=True, price=20, type='o')
        player.magic.add_spell(dispell)

        player.magic.cast_spell(dispell, player)
        self.assertFalse(PlayerSpellDue.objects.filter(player=player))

    def test_cure_negative(self):
        """
         Test if cure works on a negative spell
        """
        player = self._get_player()

        spell = Spell.objects.create(name='test-spell', available=True, price=10, type='n')
        cure = Spell.objects.create(name='cure', available=True, price=10)
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=spell, due=datetime.now() + timedelta(days=1))

        player.magic.add_spell(cure)
        player.magic.cast_spell(cure, player, datetime.now() + timedelta(days=1))

        self.assertFalse(PlayerSpellDue.objects.filter(player=player))  # There isn't any spell left

    def test_cure_positive(self):
        """
         Cure should not remove positive spells
        """
        player = self._get_player()

        spell = Spell.objects.create(name='test-spell', available=True, price=10, type='p')
        cure = Spell.objects.create(name='cure', available=True, price=10)
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=spell, due=datetime.now() + timedelta(days=1))

        player.magic.add_spell(cure)
        player.magic.cast_spell(cure, player, datetime.now() + timedelta(days=1))

        self.assertTrue(PlayerSpellDue.objects.filter(player=player))  # The spell is still present

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

    def test_paralyze(self):
        """
         Test if Paralyze spell works
        """
        Formula.add('chall-warranty')

        player = self._get_player()
        chall_user = player.get_extension(ChallengeUser)

        # Check if player can launch before spell is cast
        self.assertTrue(chall_user.can_launch())

        # Create and add spell to user
        paralyze = Spell.objects.create(name='challenge-cannot-challenge', available=True, price=10, percents=100, type='n')
        obs = PlayerSpellDue.objects.create(player=chall_user, source=chall_user, spell=paralyze, due=datetime.now() + timedelta(days=1))

        # Check if player has the modifier
        self.assertTrue(chall_user.magic.has_modifier('challenge-cannot-challenge'))

        # Player should not be able to launch challenge with Paralyze on
        self.assertFalse(chall_user.can_launch())

    @unittest.skip
    def test_evade(self):
        """
         Test for Evade spell
        """
        player = self._get_player()
        player2 = self._get_player(2)

        initial_points = 10

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player, 'points', initial_points)
        self.assertEqual(player.points, initial_points)

        # Create and apply evade
        evade = Spell.objects.create(name='challenge-evade', available=True, price=25, percents=100, type='p')
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=evade, due=datetime.now() + timedelta(days=1))
        self.assertTrue(player.magic.has_modifier('challenge-evade'))

        # Get 'chall-lost' expression. By default you still win 2 points when losing a challenge
        formulas = ChallengeGame.get_formulas()
        exp = formulas[1]['expression']  # this will be 'points=XX'
        index = exp.find('=') + 1  # get position of '='
        points = int(exp[index:])  # get XX (nr of points won when losing challenge)

        # Create challenge and make first player lose it
        chall = Challenge.create(user_from=player2, user_to=player, ignore_questions=True)
        chall.set_won_by_player(player2)

        # If evade spell worked losing player should have initial_points + 'chall-lost' points

        # Evade has 20% chance of activation so play challenge in loop while it activates
        while player.points != initial_points + points:
            player.points = initial_points
            chall.set_expired()
            chall = Challenge.create(user_from=player2, user_to=player, ignore_questions=True)
            chall.set_won_by_player(player2)

        # Check if final score is ok
        self.assertEqual(player.points, initial_points + points)

    def test_frenzy_win(self):
        """
         If user wins while affected by frenzy he should win frenzy.percents more points
        """
        initial_points = 100
        win_points = 10

        player_frenzy = self._get_player(1).get_extension(ChallengeUser)
        player_dummy = self._get_player(2).get_extension(ChallengeUser)

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player_frenzy, 'points', initial_points)

        formula = Formula.get('chall-won')
        formula.expression = 'points=' + str(win_points)
        formula.save()

        # Apply frenzy
        frenzy = Spell.objects.create(name='challenge-affect-scoring', available=True, price=25, percents=66, type='o')
        obs = PlayerSpellDue.objects.create(player=player_frenzy, source=player_frenzy, spell=frenzy, due=datetime.now() + timedelta(days=1))

        # Win challenge
        chall = Challenge.create(user_from=player_frenzy, user_to=player_dummy, ignore_questions=True)
        chall.set_won_by_player(player_frenzy)

        # Player should win frenzy.percents more points with frenzy applied
        target_points = initial_points + win_points + frenzy.percents / 100.0 * win_points

        self.assertEqual(player_frenzy.player_ptr.points, target_points)

    def test_frenzy_loss(self):
        """
         If user loses while affected by frenzy he should lose frenzy.percents more points
        """
        initial_points = 100
        loss_points = -10
        warranty_points = -3

        player_frenzy = self._get_player(1).get_extension(ChallengeUser)
        player_dummy = self._get_player(2).get_extension(ChallengeUser)

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player_frenzy, 'points', initial_points)

        formula = Formula.get('chall-lost')
        formula.expression = 'points=' + str(loss_points)
        formula.save()

        formula = Formula.get('chall-warranty')
        formula.expression = 'points=' + str(warranty_points)
        formula.save()

        # Apply frenzy
        frenzy = Spell.objects.create(name='challenge-affect-scoring', available=True, price=25, percents=66, type='o')
        obs = PlayerSpellDue.objects.create(player=player_frenzy, source=player_frenzy, spell=frenzy, due=datetime.now() + timedelta(days=1))

        # Win challenge with dummy player to see the amount of points lost by the player affected with frenzy
        chall = Challenge.create(user_from=player_frenzy, user_to=player_dummy, ignore_questions=True)
        chall.set_won_by_player(player_dummy)

        # Player should lose frenzy.percents more points with frenzy applied
        target_points = initial_points + loss_points + frenzy.percents / 100.0 * loss_points + warranty_points

        self.assertEqual(player_frenzy.player_ptr.points, target_points)

    def test_weakness(self):
        """
         Test for Weakness spell
        """
        initial_points = 100
        win_points = 10

        player_weakness = self._get_player(1).get_extension(ChallengeUser)
        player_dummy = self._get_player(2).get_extension(ChallengeUser)

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player_weakness, 'points', initial_points)

        formula = Formula.get('chall-won')
        formula.expression = 'points=' + str(win_points)
        formula.save()

        # Apply weakness
        weakness = Spell.objects.create(name='challenge-affect-scoring-lost', available=True, price=10, percents=-66, type='n')
        obs = PlayerSpellDue.objects.create(player=player_weakness, source=player_weakness, spell=weakness, due=datetime.now() + timedelta(days=1))

        # Win challenge with player_weakness
        chall = Challenge.create(user_from=player_weakness, user_to=player_dummy, ignore_questions=True)
        chall.set_won_by_player(player_weakness)

        # Player should win weakness.percents less points with weakness applied
        target_points = initial_points + win_points + weakness.percents / 100.0 * win_points
        self.assertEqual(player_weakness.player_ptr.points, target_points)

    def test_charge(self):
        """
         Test for Charge spell
        """
        initial_points = 100
        win_points = 10

        player_charge = self._get_player(1).get_extension(ChallengeUser)
        player_dummy = self._get_player(2).get_extension(ChallengeUser)

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player_charge, 'points', initial_points)

        formula = Formula.get('chall-won')
        formula.expression = 'points=' + str(win_points)
        formula.save()

        # Apply charge
        charge = Spell.objects.create(name='challenge-affect-scoring-won', available=True, price=10, percents=33, type='p')
        obs = PlayerSpellDue.objects.create(player=player_charge, source=player_charge, spell=charge, due=datetime.now() + timedelta(days=1))

        chall = Challenge.create(user_from=player_charge, user_to=player_dummy, ignore_questions=True)
        chall.set_won_by_player(player_charge)

        # Player should win weakness.percents more points with charge applied
        target_points = initial_points + win_points + charge.percents / 100.0 * win_points
        self.assertEqual(player_charge.player_ptr.points, target_points)

    def test_weakness_and_charge(self):
        """
         If both Weakness and Charge are active, a player should win weakness.percents + charge.percents less/more points
         after winning a challenge
        """
        initial_points = 100
        win_points = 10

        player = self._get_player(1).get_extension(ChallengeUser)
        player_dummy = self._get_player(2).get_extension(ChallengeUser)

        scoring.setup_scoring()
        Coin.add('points')
        scoring.score_simple(player, 'points', initial_points)

        formula = Formula.get('chall-won')
        formula.expression = 'points=' + str(win_points)
        formula.save()

        # Apply charge
        charge = Spell.objects.create(name='challenge-affect-scoring-won', available=True, price=10, percents=33, type='p')
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=charge, due=datetime.now() + timedelta(days=1))

        # Apply weakness
        weakness = Spell.objects.create(name='challenge-affect-scoring-won', available=True, price=10, percents=-66, type='p')
        obs = PlayerSpellDue.objects.create(player=player, source=player, spell=weakness, due=datetime.now() + timedelta(days=1))

        chall = Challenge.create(user_from=player, user_to=player_dummy, ignore_questions=True)
        chall.set_won_by_player(player)

        percents = (charge.percents + weakness.percents) / 100.0
        target_points = initial_points + win_points + percents * win_points

        self.assertEqual(player.player_ptr.points, target_points)

    def test_blind(self):
        """
        Test for Blind spell
        """

        # Create a question and a test user
        super_user = self._get_superuser()
        qotd_user = self._get_player(1)
        qotd_user = qotd_user.get_extension(QotdUser)
        scoring.setup_scoring()

        question = _make_question_for_today(super_user, 'question1')

        c = Client()
        c.login(username='testuser1', password='test')

        # Cast blind on qotd_user
        blind = Spell.objects.create(name='qotd-blind', available=True, price=10, type='n')
        PlayerSpellDue.objects.create(player=qotd_user, source=qotd_user, spell=blind, due=datetime.now() + timedelta(days=1))
        self.assertTrue(qotd_user.magic.has_modifier('qotd-blind'))

        # Check if it blocks the user from answering the Question of the Day
        response = c.get(reverse('qotd_index_view'), follow=True)
        self.assertContains(response, "You have been blinded, you cannot answer to the Question of the Day")


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


class TestMagicViews(WousoTest):
    def setUp(self):
        super(TestMagicViews, self).setUp()
        self.p1 = self._get_player(1)
        self.p2 = self._get_player(2)
        self.p1.points = 500
        self.p1.save()
        self.spell_1 = Spell.objects.create(name='spell1', title='Spell no. 1')
        self.spell_2 = Spell.objects.create(name='spell2', title='Spell no. 2')
        self.c = Client()
        self.c.login(username='testuser1', password='test')
        self.activity = Activity.objects.create(user_from=self.p1, user_to=self.p2,
                                                action='gold-won')
        scoring.setup_scoring()

    def test_buy_spell(self):
        Coin.add('gold')
        Formula.add('buy-spell', expression="gold=-{price}")
        spell = Spell.objects.create(name='test-spell', available=True, price=10)
        player = User.objects.create_user('test', 'test@a.ro', password='test').get_profile()

        scoring.score_simple(player, 'gold', 100)
        self.assertEqual(player.coins['gold'], 100)

        response = self.client.get(reverse('bazaar_home'))
        self.assertTrue('test-spell' in response.content)

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('bazaar_buy', kwargs={'spell': spell.id}))
        self.assertFalse('error' in response.content)

        player = Player.objects.get(user__username='test')
        self.assertEqual(player.coins['gold'], 90)

    def test_bazaar_view(self):
        response = self.c.get(reverse('bazaar_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bazaar')
        self.assertContains(response, 'Exchange')
        self.assertContains(response, 'Rate')
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')
        self.assertContains(response, 'Spell no. 1')
        self.assertContains(response, 'Spell no. 2')

    def test_bazaar_exchange_success_message(self):
        data = {'points': 10}
        response = self.c.post(reverse('bazaar_exchange'), data)
        self.assertContains(response, _('Converted successfully'))

    def test_bazaar_exchange_error_message(self):
        data = {'points': 1000}
        response = self.c.post(reverse('bazaar_exchange'), data)
        self.assertContains(response, _('Insufficient points'))
        response = self.c.get(reverse('bazaar_exchange'))
        self.assertContains(response, _('Expected post'))

    def test_magic_cast_error_message(self):
        data = {'days': 10, 'spell': self.spell_1.id}
        self.p1.magic.add_spell(self.spell_1)
        response = self.c.post(reverse('magic_cast', args=[self.p2.id]), data)
        self.assertContains(response, _('Invalid number of days'))
