from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from models import TeamQuestGroup, TeamQuestUser


class TeamQuestTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='_test_user')
        self.user = self.user.get_profile().get_extension(TeamQuestUser)

    def test_is_head(self):
        group = TeamQuestGroup.create(head=self.user, name='_test_group')
        self.assertTrue(self.user.is_head())

    def test_is_added(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        self.assertTrue(self.user.group is group)
        self.assertTrue(self.user in group.users.all())

    def test_is_removed(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        self.assertTrue(self.user in group.users.all())

        group.remove_user(self.user)
        self.assertTrue(self.user not in group.users.all())
        self.assertTrue(self.user.group is None)

    def test_is_deleted(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.remove_user(p)
        check = 1

        try:
            group = TeamQuestGroup.objects.get(name='_test_group')
            check = 0
        except TeamQuestGroup.DoesNotExist:
            self.assertTrue(p.group is None)

        self.assertEqual(check, 1)

    def test_is_promoted(self):
        p = User.objects.create(username="_test_head")
        p = p.get_profile().get_extension(TeamQuestUser)
        group = TeamQuestGroup.create(head=p, name='_test_group')
        group.add_user(self.user)

        group.promote_to_head(self.user)
        self.assertTrue(self.user.is_head())

        group.remove_user(self.user)
        self.assertTrue(p.is_head())
