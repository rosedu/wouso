import unittest
import django.test
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import UserProfile
from wouso.core import scoring
from wouso.core.qpool.models import Question, Schedule, Tag, Category


class QotdTestCase(unittest.TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)
        scoring.setup()

    def tearDown(self):
        #self.user.get_profile().delete()
        #self.user.delete()
        pass

    def _get_foo_question(self, correct=2):
        """ Return a Question object selected for Today """
        class Question: pass
        class Answer: pass
        q = Question()
        q.text = 'How many'
        q.answers = []
        for i in range(4):
            a = Answer()
            a.id, a.text, a.correct = i, str(i), True if i == correct else False
            q.answers.append(a)
        return q

    def testUserCreate(self):
        user,new = User.objects.get_or_create(username='_test2')

        profile = user.get_profile()

        self.assertTrue(isinstance(profile, UserProfile))
        self.assertTrue(isinstance(profile.get_extension(QotdUser), QotdUser))

        user.delete()

    def testAnswered(self):
        correct = 2
        q = self._get_foo_question(correct)

        h1 = scoring.history_for(self.user, QotdGame)

        QotdGame.answered(self.qotd_user, q, correct - 1)
        # Check if history didn't change
        self.assertEqual(len(h1), len(scoring.history_for(self.qotd_user, QotdGame)))

        # Answer correctly
        self.qotd_user.reset_answered()

        QotdGame.answered(self.qotd_user, q, correct)
        # History changed
        h2 = scoring.history_for(self.qotd_user, QotdGame)
        self.assertEqual(len(h1) + 1, len(h2))

        coins = scoring.user_coins(self.qotd_user)
        self.assertEqual(coins['points'], 3)

def _make_question_for_today(user, text):
    category = Category(name='qotd')
    question = Question(text=text, proposed_by=user, category=category, active=1)
    question.save()
    sched = Schedule(question=question)
    sched.save()

class PageTests(django.test.TestCase):

    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.set_password('_test_pw')
        self.user.save()
        profile = self.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)
        scoring.setup()
        self.client.login(username='_test', password='_test_pw')

    def testNoQuestion(self):
        response = self.client.get('/g/qotd/')
        self.assertContains(response, 'No question for today.')

    def testCorrectAnswer(self):
        _make_question_for_today(user=self.user, text="what is the question?")
        response = self.client.get('/g/qotd/')
        self.assertContains(response, 'No question for today.', 0)
        self.assertContains(response, 'what is the question?')
