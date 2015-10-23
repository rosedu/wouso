from django.test.client import Client
from django.core.urlresolvers import reverse

from wouso.core.tests import WousoTest
from wouso.interface.forum.models import Category


class ForumViewsTest(WousoTest):
    def setUp(self):
        super(ForumViewsTest, self).setUp()
        self.admin = self._get_superuser()
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def test_forum_view(self):
        response = self.client.get(reverse('forums_overview'))
        self.assertContains(response,"Forums")

    def test_category_view(self):
        category = Category.objects.create (name="aCategory")
        response = self.client.get(reverse('forums_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aCategory')

