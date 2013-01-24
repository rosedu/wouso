from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from wouso.core.tests import WousoTest

class TestInterface(WousoTest):
    def test_homepage_anonymous(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_homepage_player(self):
        user = User.objects.create_user('test', 'test')
        self.client.login(username='test', password='test')
        self.test_homepage_anonymous()

    def test_profile_page(self):
        admin = self._get_superuser()
        self._client_superuser()
        response = self.client.get(reverse('player_profile', kwargs=dict(id=admin.id)))
        self.assertEqual(response.status_code, 200)

    def test_jenkins(self):
        self.assertTrue(True)