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
