from django.core.cache import cache
import unittest
from datetime import datetime
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from wouso.core.magic.models import Spell, SpellHistory, ArtifactGroup, Artifact
from wouso.core.qpool.models import Category, Tag, Question, Answer
from wouso.core.scoring.models import Formula
from wouso.core.security.models import Report
from wouso.core.tests import WousoTest
from wouso.core.user.models import Race, PlayerGroup
from wouso.games.quest.models import Quest


class addPlayerTestCase(TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test1', is_staff=True, is_superuser=True)
        self.user.set_password('secret')
        self.user.save()

    def test_add_user(self):
        old_number = len(User.objects.all())
        self.client = Client()
        self.client.login(username='_test1', password='secret')

        data = {'username': '_test2', 'password': 'secret', 'confirm_password': 'secret'}
        resp = self.client.post(reverse('add_player'), data)
        new_number = len(User.objects.all())

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(old_number + 1, new_number)


class CpanelViewsTest(WousoTest):
    def setUp(self):
        super(CpanelViewsTest, self).setUp()
        self.admin = self._get_superuser()
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def test_formulas_view(self):
        Formula.objects.create(name='test_formula1', expression='points=1234',
                               description='First formula of the game')
        Formula.objects.create(name='test_formula2', expression='points=1234',
                               description='Second formula of the game')
        response = self.client.get(reverse('formulas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_formula1')
        self.assertContains(response, 'test_formula2')
        self.assertContains(response, 'points=1234', 2)

    def test_edit_formula_view_get(self):
        formula = Formula.objects.create(name='test_formula1', expression='points=1234',
                                         description='First formula of the game')
        response = self.client.get(reverse('edit_formula', args=[formula.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="test_formula1"')
        self.assertContains(response, 'value="points=1234"')
        self.assertContains(response, 'First formula of the game')

    def test_edit_formula_view_post(self):
        formula = Formula.objects.create(name='test_formula1', expression='points=1234',
                                         description='First formula of the game')
        data = {'name': 'test_formula2', 'expression': 'points=4321',
                'description': 'Second formula of the game'}
        response = self.client.post(reverse('edit_formula', args=[formula.pk]), data)
        self.assertEqual(response.status_code, 302)
        updated_formula = Formula.objects.get(pk=formula.pk)
        self.assertEqual(updated_formula.name, 'test_formula2')
        self.assertEqual(updated_formula.expression, 'points=4321')
        self.assertEqual(updated_formula.description, 'Second formula of the game')

    def test_add_formula_view_get(self):
        response = self.client.get(reverse('add_formula'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Formula')
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Expression')
        self.assertContains(response, 'Description')

    def test_add_formula_view_post(self):
        # Check the view with a valid form
        data = {'name': 'test_formula1', 'expression': 'points=4321',
                'description': 'Test Formula'}
        response = self.client.post(reverse('add_formula'), data)
        self.assertEqual(response.status_code, 302)
        formulas = Formula.objects.all()
        self.assertEqual(len(formulas), 1)
        formula = formulas[0]
        self.assertEqual(formula.name, 'test_formula1')
        self.assertEqual(formula.expression, 'points=4321')
        self.assertEqual(formula.description, 'Test Formula')

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('add_formula'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_spells_view(self):
        spell1 = Spell.objects.create(name='spell1', title='Spell no. 1')
        spell2 = Spell.objects.create(name='spell2', title='Spell no. 2')
        spell3 = Spell.objects.create(name='spell3', title='Spell no. 3')
        user1 = self._get_player(1)
        user2 = self._get_player(2)
        SpellHistory.objects.create(type='b', user_from=user1, spell=spell1)
        SpellHistory.objects.create(type='b', user_from=user1, spell=spell2)
        SpellHistory.objects.create(type='b', user_from=user2, spell=spell1)
        SpellHistory.objects.create(type='u', user_from=user2, user_to=user1,
                                    spell=spell1)
        response = self.client.get(reverse('spells'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spell no. 1')
        self.assertContains(response, 'Spell no. 2')
        self.assertContains(response, 'Spell no. 3')
        self.assertContains(response, 'Spell History')
        self.assertContains(response, '<td> 1 </td>', 3)
        self.assertContains(response, '<td> 2 </td>')
        self.assertContains(response, '<td> 3 </td>')

    def test_edit_spell_view_get(self):
        spell = Spell.objects.create(name='spell1', title='Spell no. 1')
        response = self.client.get(reverse('edit_spell', args=[spell.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit spell')
        self.assertContains(response, 'spell1')
        self.assertContains(response, 'Spell no. 1')

    def test_edit_spell_view_post(self):
        # Check the view with an invalid form
        spell = Spell.objects.create(name='spell1', title='Spell no. 1')
        data = {'name': 'updated_spell', 'title': 'Spell was updated'}
        response = self.client.post(reverse('edit_spell', args=[spell.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        # Check the view with a valid form
        data.update({'percents': 80, 'level_required': 4,
                     'type': 'o', 'due_days': 5,
                     'price': 40})
        response = self.client.post(reverse('edit_spell', args=[spell.pk]), data)
        spell = Spell.objects.get(pk=spell.pk)
        self.assertEqual(spell.name, 'updated_spell')
        self.assertEqual(spell.title, 'Spell was updated')

    def test_add_spell_get(self):
        response = self.client.get(reverse('add_spell'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Spell')

    def test_add_spell_post(self):
        # Check the view with a valid form
        data = {'name': 'spell1', 'title': 'Spell no. 1',
                'percents': 80, 'level_required': 4, 'price': 40,
                'type': 'o', 'due_days': 5}
        response = self.client.post(reverse('add_spell'), data)
        self.assertEqual(response.status_code, 302)
        spells = Spell.objects.all()
        self.assertEqual(len(spells), 1)
        spell = spells[0]
        self.assertEqual(spell.name, 'spell1')
        self.assertEqual(spell.title, 'Spell no. 1')
        self.assertEqual(spell.level_required, 4)

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('add_spell'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_qpool_tag_questions_view_get(self):
        tag1 = Tag.objects.create(name='tag1', active=True)
        tag2 = Tag.objects.create(name='tag2', active=True)
        q1 = Question.objects.create(text='Text for question1')
        q1.tags.add(tag1)
        q1.save()
        q2 = Question.objects.create(text='Text for question2')
        response = self.client.get(reverse('tag_questions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Text for question1')
        self.assertContains(response, 'Text for question2')
        self.assertContains(response, 'tag1')
        self.assertContains(response, 'tag2')

    def test_qpool_tag_questions_view_post(self):
        tag1 = Tag.objects.create(name='tag1', active=True)
        tag2 = Tag.objects.create(name='tag2', active=True)
        q1 = Question.objects.create(text='Text for question1')
        q1.tags.add(tag1)
        q1.save()
        q2 = Question.objects.create(text='Text for question2')

        # Check the view with a valid form
        data = {'tag': [str(tag2.pk)], 'questions': [str(q1.pk), str(q2.pk)]}
        response = self.client.post(reverse('tag_questions'), data)
        self.assertContains(response, 'Successfully tagged 2 question(s)')
        tag1 = Tag.objects.get(name='tag1')
        self.assertEqual(len(tag1.question_set.all()), 1)
        tag2 = Tag.objects.get(name='tag2')
        self.assertEqual(len(tag2.question_set.all()), 2)

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('tag_questions'), data)
        self.assertContains(response, 'This field is required')

    def test_qpool_managetags_view(self):
        tag1 = Tag.objects.create(name='tag1', active=True)
        tag2 = Tag.objects.create(name='tag2', active=True)
        response = self.client.get(reverse('qpool_manage_tags'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tag1')
        self.assertContains(response, 'tag2')
        self.assertContains(response, 'Manage tags')

    def test_qpool_edit_tag_view_get(self):
        tag1 = Tag.objects.create(name='tag1', active=True)
        response = self.client.get(reverse('qpool_edit_tag', args=[tag1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit tag')
        self.assertContains(response, 'tag1')

    def test_qpool_edit_tag_view_post(self):
        tag1 = Tag.objects.create(name='tag1', active=True)

        # Check the view with a valid form
        data = {'name': 'tag_updated', 'active': True}
        response = self.client.post(reverse('qpool_edit_tag', args=[tag1.pk]), data)
        self.assertEqual(response.status_code, 302)
        tag = Tag.objects.get(pk=tag1.pk)
        self.assertEqual(tag.name, 'tag_updated')
        self.assertTrue(tag.active)

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('qpool_edit_tag', args=[tag1.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_artifact_home_view(self):
        art_group = ArtifactGroup.objects.create(name='Default')
        artifact1 = Artifact.objects.create(name='artifact_test_1', group=art_group)
        artifact2 = Artifact.objects.create(name='artifact_test_2', group=art_group)
        response = self.client.get(reverse('artifact_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Artifacts')
        self.assertContains(response, 'artifact_test_1')
        self.assertContains(response, 'artifact_test_2')

    def test_add_player_view_get(self):
        response = self.client.get(reverse('add_player'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Player')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')

    def test_add_player_view_post(self):
        # Check the view with a valid form
        number_of_players = len(User.objects.all())
        data = {'username': 'test1', 'password': 'test', 'confirm_password': 'test'}
        response = self.client.post(reverse('add_player'), data)
        self.assertEqual(response.status_code, 302)
        number_of_players_after_post = len(User.objects.all())
        self.assertTrue(number_of_players_after_post > number_of_players)

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('add_player'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_manage_player_view_get(self):
        p1 = self._get_player(1)
        response = self.client.get(reverse('manage_player', args=[p1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'Username')

    def test_manage_player_view_post(self):
        p1 = self._get_player(1)

        # Check the view with a valid form
        data = {'username': 'testuser_updated', 'first_name': 'testuser_name'}
        response = self.client.post(reverse('manage_player', args=[p1.pk]), data)
        self.assertEqual(response.status_code, 302)
        p1 = User.objects.get(pk=p1.pk)
        self.assertEqual(p1.username, 'testuser_updated')
        self.assertEqual(p1.first_name, 'testuser_name')

        # Check the view with an invalid form
        data = {}
        response = self.client.post(reverse('manage_player', args=[p1.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_change_password_view_get(self):
        p1 = self._get_player(1)
        response = self.client.get(reverse('change_password', args=[p1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Confirm password')

    def test_change_password_view_post(self):
        p1 = self._get_player(1)

        # Check the view with a valid form
        data = {'password': 'secret', 'confirm_password': 'secret'}
        response = self.client.post(reverse('change_password', args=[p1.pk]), data)
        p1 = self._get_player(1)
        self.assertTrue(p1.user.check_password('secret'))

         # Check the view with an invalid form
        data = {'password': 'test'}
        response = self.client.post(reverse('change_password', args=[p1.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')


    def test_races_groups_view(self):
        """ Test adds races and groups and verifies the
        following situations:
        - any added race is displayed
        - a group with no parent is displayed
        - when a race is deleted, all contained groups
        are also deleted
        """
        r1 = Race.objects.create(name='Race_test_1', can_play=True)
        r2 = Race.objects.create(name='Race_test_2', can_play=False)
        r3 = Race.objects.create(name='Race_test_3', can_play=True)
        PlayerGroup.objects.create(name='PlayerGroup_test_1', parent=r1)
        PlayerGroup.objects.create(name='PlayerGroup_test_2', parent=None)
        PlayerGroup.objects.create(name='PlayerGroup_test_3', parent=r3)
        r3.delete()
        response = self.client.get(reverse('races_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Races and groups')
        self.assertContains(response, 'Race_test_1')
        self.assertContains(response, 'Race_test_2')
        self.assertContains(response, 'PlayerGroup_test_1')
        self.assertContains(response, 'PlayerGroup_test_2')
        self.assertNotContains(response, 'Race_test_3')
        self.assertNotContains(response, 'PlayerGroup_test_3')

    def test_roles_view(self):
        user = User.objects.create(username='testuser1', password='test')
        group = Group.objects.create(name='Group_test')
        content_type = ContentType.objects.create(name='ctype_test')
        perm = Permission.objects.create(name='perm_test', content_type=content_type)
        group.permissions.add(perm)
        user.groups.add(group)
        response = self.client.get(reverse('roles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Roles')
        self.assertContains(response, 'Group_test')
        self.assertContains(response, 'perm_test')
        self.assertContains(response, 'ctype_test')

        # Check if the user is counted
        self.assertContains(response, '<td>1</td>')

    def test_reports_view(self):
        p1 = self._get_player(1)
        p2 = self._get_player(2)
        Report.objects.create(user_from=p1, user_to=p2, timestamp=datetime.now())
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reports')
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')

    def test_edit_report_view(self):
        # Check the GET method
        p1 = self._get_player(1)
        p2 = self._get_player(2)
        report = Report.objects.create(user_from=p1, user_to=p2, timestamp=datetime.now())
        response = self.client.get(reverse('edit_report', args=[report.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Report')
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')

        # Check the POST method
        self.assertEqual(report.status, 'R')
        data = {'dibs': '', 'status': 'I', 'extra': ''}
        response = self.client.post(reverse('edit_report', args=[report.pk]), data)
        self.assertEqual(response.status_code, 302)
        report_updated = Report.objects.get(pk=report.pk)
        self.assertEqual(report_updated. status, 'I')

    def test_system_message_group_message_display(self):
        pg = PlayerGroup.objects.create(name='PlayerGroup_1')
        data = {'text': 'sample message'}

        # Message is displayed when the method is POST
        response = self.client.post(reverse('system_message_group', args=[pg.pk]), data)
        self.assertContains(response, 'Message sent!')

        # Message is not displayed when the method is GET
        response = self.client.get(reverse('system_message_group', args=[pg.pk]))
        self.assertNotContains(response, 'Message sent!')

    def test_customization_view_get(self):
        response = self.client.get(reverse('customization_home'))
        self.assertContains(response, 'Customization', status_code=200)
        self.assertContains(response, 'Features', status_code=200)
        self.assertContains(response, 'Games', status_code=200)
        self.assertContains(response, 'Display', status_code=200)

    def test_customization_view_post(self):
        data = {'title': 'Custom test title'}

        # POST data
        response = self.client.post(reverse('customization_home'), data)

        # Check if data has been updated
        response = self.client.get(reverse('customization_home'))
        self.assertContains(response, 'Custom test title', status_code=200)

    def test_games_view_get(self):
        response = self.client.get(reverse('customization_games'))
        self.assertContains(response, 'Games', status_code=200)

    def test_games_view_post(self):
        data = {'disable-WorkshopGame': 'True'}
        response = self.client.post(reverse('customization_games'), data)
        response = self.client.get(reverse('customization_games'))
        self.assertContains(response, 'id="disable-WorkshopGame" checked')

    @unittest.skip  # TODO fixme
    def test_qpool_importer_view(self):
        response = self.client.get(reverse('importer'))
        chall_cat = Category.objects.get(name='challenge')
        self.assertContains(response, 'Select input file', status_code=200)
        self.assertTrue(chall_cat in response.context['categories'])

    def test_qpool_new_view_get(self):
        Category.objects.create(name='sample_category')
        response = self.client.get(reverse('add_question'))
        self.assertContains(response, 'Add question', status_code=200)
        self.assertContains(response, 'Insert question text')
        self.assertContains(response, 'Select category')
        self.assertContains(response, 'sample_category')

    def test_qpool_new_category_ok(self):
        # Test question with normal text
        Category.objects.create(name='sample_category')
        data = {'text': 'sample text for test question',
                'category': 'sample_category',
                'answer_type': 'R',
                'answer_1': 'sample answer',
                'correct_1': 'on',
                'active_1': 'on'}
        response = self.client.post(reverse('add_question'), data)
        self.assertTrue(Question.objects.get(category__name='sample_category'))

        # Test question with rich text
        Category.objects.create(name='sample_category_2')
        data = {'rich_text': '<p><b>sample rich text</b></p>',
                'category': 'sample_category_2',
                'answer_type': 'R',
                'rich_answer_1': '<i>sample_answer</i>',
                'rich_correct_1': 'on',
                'rich_active_1': 'on'}
        response = self.client.post(reverse('add_question'), data)
        self.assertTrue(Question.objects.get(category__name='sample_category_2'))

    @unittest.skip
    # FIXME: If not entering all fields the question home page should add
    # an "Invalid" string.
    def test_qpool_new_no_answer_invalid(self):
        Category.objects.create(name='sample_category')
        data = {'text': 'sample text for test question',
                'category': 'sample_category',
                'answer_type': 'R'}
        response = self.client.post(reverse('question_new'), data)
        response = self.client.get(reverse('qpool_home'))
        self.assertContains(response, 'Invalid')

    def test_qpool_new_question_ok(self):
        Category.objects.create(name='sample_category')

        # Test question with normal text
        data = {'text': 'sample text for test question',
                'category': 'sample_category',
                'answer_type': 'R',
                'answer_1': 'sample_response',
                'correct_1': 'on',
                'active_1': 'on'}
        response = self.client.post(reverse('add_question'), data)
        self.assertTrue(Question.objects.get(text='sample text for test question'))

        # Test question with rich text
        data = {'rich_text': '<p><b>sample rich text</b></p>',
                'category': 'sample_category',
                'answer_type': 'R',
                'rich_answer_1': '<i>sample_answer</i>',
                'rich_correct_1': 'on',
                'rich_active_1': 'on'}
        response = self.client.post(reverse('add_question'), data)
        self.assertTrue(Question.objects.get(rich_text='<p><b>sample rich text</b></p>'))

    def test_status_view(self):
        # Create dummy objects
        race = Race.objects.create(name='Race_test_1', can_play=True)

        for i in range(5):
            Question.objects.create(text='Question number %d' % i)
            Quest.objects.create(start=datetime.now(), end=datetime.now())

        for i in range(6):
            player = User.objects.create(username='Student%d' % i, password='test').get_profile()
            player.race = race
            player.save()
            ArtifactGroup.objects.create(name='ArtifactGroup%d' % i)

        response = self.client.get(reverse('status'))

        # Check if the required information is displayed
        self.assertContains(response, '6 users can play')
        self.assertContains(response, '5 total questions')
        self.assertContains(response, 'No quest active. Total: 5')
        self.assertContains(response, 'ArtifactGroup3')

    def test_karma_view(self):
        race = Race.objects.create(name='Race_test', can_play=True)
        group = PlayerGroup.objects.create(name='Group_test', parent=race)
        data = {'races': race, 'groups': group}

        response = self.client.get(reverse('karma'), kwargs=data)

        self.assertContains(response, race)
        self.assertContains(response, group)

    def test_karma_group_view(self):
        group = PlayerGroup.objects.create(name='Group_test')
        player = User.objects.create(username='test_user',
                                     password='test').get_profile()
        group.players.add(player)

        response = self.client.get(reverse('karma_group', args=[group.id]))

        self.assertContains(response, group)
        self.assertContains(response, player)
