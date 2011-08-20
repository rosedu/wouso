import unittest
from django.test.client import Client
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import UserProfile
from wouso.core import scoring

class QotdTestCase(unittest.TestCase):        
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.set_password('_test_pw')
        self.user.save()
        profile = self.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)
        scoring.setup()
        
    def tearDown(self):
        self.user.delete()
        
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
        user = User.objects.create()
        
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

    def testNoQuestion(self):
        c = Client()
        c.login(username='_test', password='_test_pw')
        response = c.get('/g/qotd/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No question for today.' in response.content)
