from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from models import SpecialQuestUser, SpecialQuestGroup, SpecialQuestGame, SpecialQuestTask
from wouso.core.tests import WousoTest

class TestSpecialQuestView(WousoTest):
    def setUp(self):
        self.user = self._get_player(1).get_extension(SpecialQuestUser)
        self.admin = self._get_superuser()
        start = datetime.now()
        end = start + timedelta(days=1)
        self.special_quest1= SpecialQuestTask.objects.create(start_date=start, end_date=end,
                                                             name='special_quest1', value=400)
        self.special_quest2= SpecialQuestTask.objects.create(start_date=start, end_date=end,
                                                             name='special_quest2', value=800)
        self.c = Client()

    def test_cpanel_home_view(self):
        self.c.login(username='admin', password='admin')
        response = self.c.get(reverse('specialquest_home'))
        self.assertContains(response, '400')
        self.assertContains(response, '800')
        self.assertContains(response, 'special_quest1')
        self.assertContains(response, 'special_quest2')

    def test_cpanel_home_view_has_restricted_access(self):
        self.c.login(username='testuser1', password='test')
        response = self.c.get(reverse('specialquest_home'))
        # Check if user has been redirected
        self.assertEqual(response.status_code, 302)

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
