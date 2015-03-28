from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from wouso.core.qpool.models import Question, Answer, Category

from models import *


class TeamQuestGroupTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)

    def test_is_head(self):
        group = TeamQuestGroup.create(head=self.user, name='_test_group')
        self.assertTrue(self.user.is_head())

    def test_is_added(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        self.assertTrue(self.user.group is group)
        self.assertTrue(self.user in group.users.all())

    def test_is_removed(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        self.assertTrue(self.user in group.users.all())

        group.remove_user(self.user)
        self.assertTrue(self.user not in group.users.all())
        self.assertTrue(self.user.group is None)

    def test_is_deleted(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.remove_user(p)
        check = 1

        try:
            group = TeamQuestGroup.objects.get(name='_test_group')
            check = 0
        except TeamQuestGroup.DoesNotExist:
            self.assertTrue(p.group is None)

        self.assertEqual(check, 1)

    def test_is_promoted(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        group.promote_to_head(self.user)
        self.assertTrue(self.user.is_head())

        group.remove_user(self.user)
        self.assertTrue(p.is_head())


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

        level.add_question(self.question2)
        self.assertTrue(self.question2 in level.questions.all())

        level.remove_question(self.question1)
        self.assertTrue(self.question1 not in level.questions.all())
