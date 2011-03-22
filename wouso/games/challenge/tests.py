import unittest
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import UserProfile
from wouso.core import scoring

class ChallengeTestCase(unittest.TestCase):        
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.chall_user = self.user.get_profile().get_extension(ChallengeUser)
        self.user2 = User.objects.create(username='_test2')
        self.user2.save()
        self.chall_user2 = self.user2.get_profile().get_extension(ChallengeUser)
        scoring.setup()
        
    def tearDown(self):
        self.user.delete()
        self.user2.delete()
        
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
        self.assertTrue(isinstance(profile.get_extension(ChallengeUser), ChallengeUser))
        
        user.delete()
        
    def testLaunch(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2)
        
        self.assertTrue(isinstance(chall, Challenge))
        self.assertTrue(chall.is_launched())
        
        chall.refuse()
        self.assertTrue(chall.is_refused())
