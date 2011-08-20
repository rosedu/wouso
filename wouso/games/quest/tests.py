import unittest
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import UserProfile
from wouso.core import scoring

class QuestTestCase(unittest.TestCase):        
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.quest_user = profile.get_extension(QuestUser)
        scoring.setup()
        
    def tearDown(self):
        self.user.delete()

    def _get_foo_question(self, correct=2):
        """ Return a Question """
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
        self.assertTrue(isinstance(profile.get_extension(QuestUser), QuestUser))
        
        user.delete()

