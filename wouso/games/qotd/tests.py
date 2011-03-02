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
        profile, new = UserProfile.objects.get_or_create(user=user)
        
        new = QotdUser.objects.create(user=user)
        self.assertEqual(new, profile.get_extension(QotdUser))
