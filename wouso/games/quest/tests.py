import unittest
from django.contrib.auth.models import User
from models import *
from wouso.core.user.models import Player
from wouso.core import scoring

class QuestTestCase(unittest.TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.quest_user = profile.get_extension(QuestUser)
        scoring.setup_scoring()

    def tearDown(self):
        #self.user.delete()
        pass

