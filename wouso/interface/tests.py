from django.contrib.auth.models import User
from django.test import TestCase

class TestInterface(TestCase):
    def test_homepage_anonymous(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_homepage_player(self):
        user = User.objects.create_user('test', 'test')
        self.client.login(username='test', password='test')
        self.test_homepage_anonymous()

    def test_jenkins(self):
        self.assertTrue(True)