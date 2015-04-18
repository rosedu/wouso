from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _
from django.test.client import Client

from wouso.core.qpool.models import Question, Answer, Category
from wouso.core.tests import WousoTest

from models import *
from views import *


def _create_quest(number_of_levels):
    category = Category.add('quest')

    questions = []
    for index in range(number_of_levels * (number_of_levels + 1) / 2):
        question = Question.objects.create(text='question'+str(index+1), answer_type='F',
                                           category=category, active=True)
        questions.append(question)
        answer = Answer.objects.create(text='answer'+str(index+1), correct=True, question=question)

    levels = []
    # The start index of the questions sequence that goes in a level
    base = 0
    for index in range(number_of_levels):
        level = TeamQuestLevel.create(quest=None, bonus=0,
                                      questions=questions[base:base+number_of_levels-index])
        levels.append(level)
        base += number_of_levels - index

    quest = TeamQuest.create(title="_test_quest", start_time=datetime.datetime.now(),
                             end_time=datetime.datetime(2030,12,25), levels=levels)
    return quest


class TeamQuestGroupTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)
        self.owner = User.objects.create(username="_test_group_owner")
        self.owner = self.owner.get_profile().get_extension(TeamQuestUser)

    def test_user_is_group_owner(self):
        group = TeamQuestGroup.create(group_owner=self.user, name='_test_group')

        self.assertTrue(self.user.is_group_owner())

    def test_add_user_to_group(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        group.add_user(self.user)

        self.assertTrue(self.user.group == group)
        self.assertTrue(self.user in group.users.all())

    def test_remove_user_from_group(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        group.add_user(self.user)
        group.remove_user(self.user)

        self.assertTrue(self.user not in group.users.all())
        self.assertTrue(self.user.group is None)

    def test_delete_group(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        group.remove_user(self.owner)

        self.assertEqual(TeamQuestGroup.objects.filter(name='_test_group').count(), 0)

    def test_no_owner_for_deleted_group(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        group.remove_user(self.owner)

        self.assertTrue(self.owner.group is None)

    def test_user_is_promoted(self):
        group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        group.add_user(self.user)
        group.promote_to_group_owner(self.user)

        self.assertTrue(self.user.is_group_owner())

    def test_user_is_promoted_on_owner_removal(self):
        group = TeamQuestGroup.create(group_owner=self.user, name='_test_group')

        group.add_user(self.owner)
        group.remove_user(self.user)

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

    def test_create_level(self):
        level = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1, self.question2])

        self.assertEqual(level.bonus, 50)
        self.assertEqual(level.questions.count(), 2)
        self.assertTrue(self.question1 in level.questions.all())
        self.assertTrue(self.question2 in level.questions.all())

    def test_add_question_to_level(self):
        level = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1])

        level.add_question(self.question2)

        self.assertTrue(self.question2 in level.questions.all())

    def test_remove_question_from_level(self):
        level = TeamQuestLevel.create(quest=None, bonus=50, questions=[self.question1, self.question2])

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

        self.assertTrue(self.level1 in quest.levels.all())
        self.assertTrue(self.level2 in quest.levels.all())

    def test_quest_end_time_before_start_time(self):
        pass


class TeamQuestStatusTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create(username='_test_user')
        self.owner = self.owner.get_profile().get_extension(TeamQuestUser)
        self.group = TeamQuestGroup.create(group_owner=self.owner, name='_test_group')

        self.quest = _create_quest(5)

    def test_quest_status_create_default(self):
        pass

    def test_quest_status_create(self):
        """Testing the cascade creation of a Team Quest Status"""
        # When a status is created, for each level a level status is created
        # and for each level status a team quest question is created
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

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

    def test_quest_status_total_points(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)
        total_points = 0

        for level_status in status.levels.all():
            total_points += level_status.level.points_per_question * level_status.questions.all().count()

        self.assertEqual(total_points, status.quest.total_points)

    def test_quest_initial_progress_is_zero(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

        self.assertEqual(status.progress, 0)

    def test_quest_status_progress_partial(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

        for level_status in status.levels.all():
            for question in level_status.questions.all():
                # Progress before answering a question
                initial_progress = status.progress

                question.state = 'A'
                question.save()

                # Progress after answering a question
                later_progress = status.progress
                points_per_question = later_progress - initial_progress

                self.assertEqual(points_per_question, level_status.level.points_per_question)

    def test_quest_status_progress_100(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

        for level_status in status.levels.all():
            for question in level_status.questions.all():
                question.state = 'A'
                question.save()

        self.assertEqual(status.progress, status.quest.total_points)

    def test_level_status_index(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)
        total_levels = status.levels.all().count()
        level_indexes = []

        for level_status in status.levels.all():
            level_questions = level_status.questions.all().count()
            # Test that the index is calculated properly
            self.assertEqual(level_status.level.index, total_levels - level_questions + 1)
            # Test that the index is unique
            self.assertTrue(level_status.level.index not in level_indexes)
            level_indexes.append(level_status.level.index)

    def test_question_index(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)
        question_indexes = []
        total_levels = status.levels.all().count()

        # Precalculate the index range for questions
        lower_boundary = 1
        upper_boundary = total_levels * (total_levels + 1) / 2
        index_range = range(lower_boundary, upper_boundary + 1)

        for level_status in status.levels.all():
            for question in level_status.questions.all():
                # Test index unicity
                self.assertTrue(question.index not in question_indexes)
                # Test index in inside the range
                self.assertTrue(question.index in index_range)
                question_indexes.append(question.index)

    def test_level_status_reveal_next_level(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)
        total_levels = status.levels.all().count()

        for level_status in status.levels.all():
            if level_status.level.index != total_levels:
                # If not the last level, check next level by index
                self.assertEqual(level_status.next_level.level.index - 1, level_status.level.index)
            else:
                # If last level, check next_level is none
                self.assertEqual(level_status.next_level, None)

    # def test_level_status_unlock_questions(self):
    #     status = TeamQuestStatus.create(group=self.group, quest=self.quest)
    #     total_levels = status.levels.all().count()

    #     for level_status in status.levels.all():
    #         # The first level is a special case, as all the questions are unlocked
    #         if level_status.level.index == 1:
    #             for question in level_status.questions.all():
    #                 self.assertTrue(question in level_status.unlocked_questions)

    #         else:
    #             for question in level_status.questions.all():
    #                 # Check if question is not in unlocked_questions
    #                 self.assertTrue(question not in level_status.unlocked_questions)
    #                 # Unlock current question
    #                 question.lock = 'U'
    #                 question.save()
    #                 # Check if it now is in unlocked_questions
    #                 self.assertTrue(question in level_status.unlocked_questions)

    def test_level_status_is_completed(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

        for level_status in status.levels.all():
            # Check that a level is completed only after all the questions are answered
            for question in level_status.questions.all():
                self.assertEqual(level_status.completed, False)
                question.state = 'A'
                question.save()

            self.assertEqual(level_status.completed, True)

    def test_level_times_completed_once(self):
        status = TeamQuestStatus.create(group=self.group, quest=self.quest)

        level_status = status.levels.all()[0]
        for question in level_status.questions.all():
            question.state = 'A'
            question.save()

        self.assertTrue(level_status.level.times_completed, 1)

    def test_level_times_completed(self):
        owner = User.objects.create(username='_test_another_user')
        owner = owner.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(group_owner=owner, name='_test_another_group')
        status1 = TeamQuestStatus.create(group=self.group, quest=self.quest)
        status2 = TeamQuestStatus.create(group=group, quest=self.quest)

        level_status1 = status1.levels.all()[0]
        level_status2 = TeamQuestLevelStatus.objects.get(level=level_status1.level, quest_status=status2)
        for question in level_status1.questions.all():
            question.state = 'A'
            question.save()
        for question in level_status2.questions.all():
            question.state = 'A'
            question.save()

        self.assertEqual(level_status2.level.times_completed, 2)

    def test_quest_status_time_finished_before_time_started(self):
        pass


class TeamQuestGameTest(TestCase):
    def setUp(self):
        category = Category.add('quest')
        self.quest = TeamQuest.create(title="_test_quest", start_time=datetime.datetime.now(),
                                 end_time=datetime.datetime(2030,12,25), levels=[])

    def test_active_quest_exists(self):
        quest = TeamQuestGame.get_current()
        self.assertEqual(quest, self.quest)

    def test_no_active_quest(self):
        self.quest.end_time = datetime.datetime(2010,12,25)
        self.quest.save()

        quest = TeamQuestGame.get_current()

        self.assertEqual(quest, None)


class TeamQuestViewsTest(WousoTest):

    def setUp(self):
        super(TeamQuestViewsTest, self).setUp()
        self.player1 = self._get_player(1).get_extension(TeamQuestUser)
        self.player2 = self._get_player(2).get_extension(TeamQuestUser)
        self.c = Client()
        self.c.login(username='testuser1', password='test')
        self.quest = _create_quest(5)
        self.group = TeamQuestGroup.create(group_owner=self.player2, name='_test_group')

    def test_sidebar_view_end_time_has_passed(self):
        context = {'user': self.player1.user}

        self.quest.end_time = datetime.datetime(1234,12,25)
        self.quest.save()
        sidebar = sidebar_widget(context)

        self.assertTrue("There is no active quest." in sidebar)

    def test_sidebar_view_quest_no_group(self):
        context = {'user': self.player1.user}

        sidebar = sidebar_widget(context)

        self.assertTrue("There is an active quest, but you need a team to play." in sidebar)

    def test_sidebar_view_not_started(self):
        context = {'user': self.player2.user}
        
        sidebar = sidebar_widget(context)

        self.assertTrue("Start quest" in sidebar)

    def test_sidebar_view_started(self):
        context = {'user': self.player2.user}

        status = TeamQuestStatus.create(quest=self.quest, group=self.group)
        sidebar = sidebar_widget(context)

        self.assertTrue("Play quest" in sidebar)
