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

    def test_cpanel_groups_view(self):
        self.c.login(username='admin', password='admin')
        new_group = SpecialQuestGroup.create(head=self.user, name='Special Group no. 1')
        response = self.c.get(reverse('specialquest_cpanel_groups'))
        self.assertContains(response, 'Special Group no. 1')

    def test_cpanel_home_view_has_restricted_access(self):
        self.c.login(username='testuser1', password='test')
        response = self.c.get(reverse('specialquest_cpanel_groups'))
        # Check if user has been redirected
        self.assertEqual(response.status_code, 302)

    def test_cpanel_group_delete(self):
        new_group = SpecialQuestGroup.create(head=self.user, name='Special Group no. 1')
        user2 = self._get_player(2).get_extension(SpecialQuestUser)
        user3 = self._get_player(3).get_extension(SpecialQuestUser)
        new_group.players.add(user2, user3)
        user2.group = new_group
        user3.group = new_group
        user2.save()
        user3.save()
        self.c.login(username='admin', password='admin')
        self.c.get(reverse('specialquest_cpanel_group_delete', args=[new_group.pk]))

        # Check if the group is deleted
        self.assertEqual(len(SpecialQuestGroup.objects.all()), 0)

        # Check if the users don't belong to the deleted group
        users = User.objects.filter(username__contains='testuser')
        for user in users:
            specialquest_user = user.get_profile().get_extension(SpecialQuestUser)
            self.assertFalse(specialquest_user.group)

    def test_accept_group_invite(self):
        new_group = SpecialQuestGroup.create(head=self.user, name='Special Group no. 1')
        user2 = self._get_player(2).get_extension(SpecialQuestUser)
        self.c.login(username='testuser2', password='test')
        self.c.get(reverse('specialquest_accept', args=[new_group.id]))
        user2 = User.objects.get(username='testuser2').get_profile().get_extension(SpecialQuestUser)
        self.assertEqual(user2.group.name, 'Special Group no. 1')
        self.assertEqual(len(new_group.members), 2)

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
