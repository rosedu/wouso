from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase

class addPlayerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='_test', is_staff=True, is_superuser=True)
        self.user.set_password('secret')
        self.user.save()

    def test_add_user(self):
        old_number = len(User.objects.all())
        self.client = Client()
        self.client.login(username='_test', password='secret')
        User.objects.get(pk=1).is_staff
        resp = self.client.post('/cpanel/add_player/', {'username': '_test2', 'password': 'secret'})
        new_number = len(User.objects.all())

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(old_number + 1, new_number)
