from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import TestCase


class WousoTest(TestCase):
    def setUp(self):
        cache.clear()

    def _get_player(self, index=0):
        user, new = User.objects.get_or_create(username='testuser%d' % index)
        if new is True:
            user.set_password('test')
            user.save()
        return user.get_profile()

    def _get_superuser(self):
        user = User.objects.get_or_create(username='admin')[0]
        user.is_superuser = True
        user.set_password('admin')
        user.save()
        return user

    def _client_superuser(self):
        self._get_superuser()
        self.client.login(username='admin', password='admin')
