from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from models import TeamQuestGroup, TeamQuestUser


class TeamQuestTest(TestCase):
	
	def setUp(self):
		self.user = User.objects.create(username='_test_user')
		self.special_user = self.user.get_profile().get_extension(TeamQuestUser)

	def test_is_head(self):
		group = TeamQuestGroup.create(head=self.special_user, name='_test_group')
		self.assertTrue(self.special_user.is_head())

	def test_is_added(self):
		p = User.objects.create(username="_test_head")
		p = p.get_profile().get_extension(TeamQuestUser)
		group = TeamQuestGroup.create(head=p, name='_test_group')
		group.add(self.special_user)

		self.assertTrue(self.special_user.group is group)
		self.assertTrue(self.special_user in group.users.all())

	def test_is_removed(self):
		p = User.objects.create(username="_test_head")
		p = p.get_profile().get_extension(TeamQuestUser)
		group = TeamQuestGroup.create(head=p, name='_test_group')
		group.add(self.special_user)

		self.assertTrue(self.special_user in group.users.all())

		group.remove(self.special_user)
		self.assertTrue(self.special_user not in group.users.all())
		self.assertTrue(self.special_user.group is None)

	def test_is_deleted(self):
		p = User.objects.create(username="_test_head")
		p = p.get_profile().get_extension(TeamQuestUser)
		group = TeamQuestGroup.create(head=p, name='_test_group')
		group.remove(p)
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
		group.add(self.special_user)

		group.promote(self.special_user)
		self.assertTrue(self.special_user.is_head())

		group.remove(self.special_user)
		self.assertTrue(p.is_head())
