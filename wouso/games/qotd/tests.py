import unittest
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import UserProfile

class QotdTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def testUserCreate(self):
        user = User.objects.create()
        
        profile = user.get_profile()
        
        self.assertTrue(isinstance(profile, UserProfile))
        self.assertTrue(isinstance(profile.get_extension(QotdUser), QotdUser))
