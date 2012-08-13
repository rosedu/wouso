"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from models import SpecialQuestUser, SpecialQuestGroup, SpecialQuestGame

class SpecialquestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.special_user = self.user.get_profile().get_extension(SpecialQuestUser)

    def test_user_create_group(self):
        group = SpecialQuestGroup.create(head=self.special_user, name='le group')

        self.assertTrue(group)
        self.assertEqual(group.head, self.special_user)
        self.assertEqual(group.name, 'le group')
        self.assertEqual(group.owner, SpecialQuestGame.get_instance())

        self.assertTrue(self.user.get_profile() in group.players.all())

    def test_user_invite(self):
        pass

    def test_user_accept_invite(self):
        pass