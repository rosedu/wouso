from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from django.utils.translation import ugettext as _

from wouso.core.qpool.models import Question, Answer, Category
from wouso.core.tests import WousoTest

from models import *


class TeamQuestGroupTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)
        self.owner = User.objects.create(username="_test_group_owner")
        self.owner = self.owner.get_profile().get_extension(TeamQuestUser)

    def test_is_group_owner(self):
        group = TeamQuestGroup.create(group_owner=self.user, name='_test_group')
        self.user = User.objects.get(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)
        self.assertTrue(self.user.is_group_owner())

    def test_is_added(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')
        group.add_user(self.user)

        group = TeamQuestGroup.objects.get(name='_test_group')
        self.user = User.objects.get(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)

        self.assertTrue(self.user.group == group)
        self.assertTrue(self.user in group.users.all())

    def test_is_removed(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')
        group.add_user(self.user)

        group = TeamQuestGroup.objects.get(name='_test_group')
        self.user = User.objects.get(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)

        self.assertTrue(self.user in group.users.all())

        group.remove_user(self.user)

        group = TeamQuestGroup.objects.get(name='_test_group')
        self.user = User.objects.get(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)

        self.assertTrue(self.user not in group.users.all())
        self.assertTrue(self.user.group is None)

    def test_is_deleted(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')
        group.remove_user(self.owner)
        check = 1

        try:
            group = TeamQuestGroup.objects.get(name='_test_group')
            check = 0
        except TeamQuestGroup.DoesNotExist:
            self.owner = User.objects.get(username="_test_group_owner")
            self.owner = self.owner.get_profile().get_extension(TeamQuestUser)
            self.assertTrue(self.owner.group is None)

        self.assertEqual(check, 1)

    def test_is_promoted(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')
        group.add_user(self.user)
        group = TeamQuestGroup.objects.get(name='_test_group')

        group.promote_to_group_owner(self.user)
        self.user = User.objects.get(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.objects.get(name='_test_group')
        self.assertTrue(self.user.is_group_owner())

        group.remove_user(self.user)

        self.owner = User.objects.get(username="_test_group_owner")
        self.owner = self.owner.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.objects.get(name='_test_group')

        self.assertTrue(self.owner.is_group_owner())


class TeamQuestLevelTest(TestCase):

    def setUp(self):
        category = Category.add('quest')
        self.question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        self.answer1 = Answer.objects.create(text='first answer', correct=True, question=self.question1)
        self.question2 = Question.objects.create(text='question2', answer_type='F',
                                           category=category, active=True)
        self.answer2 = Answer.objects.create(text='second answer', correct=True, question=self.question2)

    def test_level_creation(self):
        level = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1, self.question2])

        self.assertEqual(level.bonus, 50)
        self.assertEqual(level.questions.count(), 2)
        self.assertTrue(self.question1 in level.questions.all())
        self.assertTrue(self.question2 in level.questions.all())

    def test_level_add_and_remove(self):
        level = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1])

        level = TeamQuestLevel.objects.get(quest=None)
        level.add_question(self.question2)
        self.assertTrue(self.question2 in level.questions.all())

        level = TeamQuestLevel.objects.get(quest=None)
        level.remove_question(self.question1)
        self.assertTrue(self.question1 not in level.questions.all())


class TeamQuestTest(TestCase):

    def setUp(self):
        category = Category.add('quest')
        self.question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        self.answer1 = Answer.objects.create(text='first answer', correct=True, question=self.question1)
        self.question2 = Question.objects.create(text='question2', answer_type='F',
                                           category=category, active=True)
        self.answer2 = Answer.objects.create(text='second answer', correct=True, question=self.question2)
        self.level1 = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1])
        self.level2 = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question2])
        self.levels = [self.level1, self.level2]

    def test_quest_create_default(self):
        pass

    def test_quest_create(self):
        quest = TeamQuest.create(title="_test_quest", start_time=datetime.datetime.now(),
                                 end_time=datetime.datetime.now(), levels=self.levels)
        quest = TeamQuest.objects.get(title="_test_quest")
        self.assertTrue(self.level1 in quest.levels.all())
        self.assertTrue(self.level2 in quest.levels.all())

        levels = TeamQuestLevel.objects.filter(quest=quest)
        self.assertTrue(self.level1 in levels)
        self.assertTrue(self.level2 in levels)

    def test_quest_end_time_before_start_time(self):
        pass


class TeamQuestStatusTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create(username='_test_user')
        self.owner = self.owner.get_profile().get_extension(TeamQuestUser)
        self.group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')
        category = Category.add('quest')
        self.question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        self.answer1 = Answer.objects.create(text='first answer', correct=True, question=self.question1)
        self.question2 = Question.objects.create(text='question2', answer_type='F',
                                           category=category, active=True)
        self.answer2 = Answer.objects.create(text='second answer', correct=True, question=self.question2)
        level1 = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1])
        level2 = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question2])
        self.levels = [level1, level2]
        self.quest = TeamQuest.create(title="_test_quest", start_time=datetime.datetime.now(),
                                 end_time=datetime.datetime.now(), levels=self.levels)

    def test_quest_status_create_default(self):
        pass

    def test_quest_status_create(self):
        """Testing the cascade creation of a Team Quest Status"""
        # When a status is created, for each level a level status is created
        # and for each level status a team quest question is created
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)
        status = TeamQuestStatus.objects.get(group=self.group, quest=self.quest)

        self.assertEqual(self.group, status.group)
        self.assertEqual(self.quest, status.quest)

        # For each level status I check that the level it points to exists in
        # the levels of the quest
        for level_status in status.levels.all():
            self.assertEqual(level_status.quest_status, status)
            self.assertTrue(level_status.level in self.quest.levels.all())

            # For each team quest question I check that the question it points
            # to exists in the questions of the level (pointed by status)
            for team_quest_question in level_status.questions.all():
                # Check if the questions on the start level are unlocked and the rest are locked
                if level_status.questions.all().count() == status.levels.all().count():
                    self.assertTrue(team_quest_question.lock == 'U')
                else:
                    self.assertTrue(team_quest_question.lock == 'L')

                self.assertEqual(team_quest_question.level, level_status)
                self.assertTrue(team_quest_question.question in level_status.level.questions.all())


    def test_quest_status_time_finished_before_time_started(self):
        pass


class TeamQuestCpanelViewsTest(WousoTest):

    def setUp(self):
        self.admin = self._get_superuser()
        self.c = Client()
        self.c.login(username='admin', password='admin')

    def test_cpanel_home_view_basic(self):
        response = self.c.get(reverse('teamquest_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add team quest')
        self.assertContains(response, 'Quests')
        self.assertContains(response, 'Groups')
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Manage')

    def test_cpanel_home_view_no_teamquests(self):
        response = self.c.get(reverse('teamquest_home'))
        self.assertContains(response, 'No Team Quests added yet!')

    def test_cpanel_home_view_list_teamquests(self):
        now = datetime.datetime.now()
        TeamQuest.objects.create(start_time=now, end_time=now+timedelta(days=1),
                                 title='TeamQuest no.1')
        TeamQuest.objects.create(start_time=now+timedelta(days=1), end_time=now+timedelta(days=2),
                                 title='TeamQuest no.2')
        # Check if Team Quest are displayed
        response = self.c.get(reverse('teamquest_home'))
        self.assertContains(response, 'TeamQuest no.1')
        self.assertContains(response, 'TeamQuest no.2')
