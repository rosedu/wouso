from django.contrib.auth.models import User
from django.test import TestCase

class WousoTest(TestCase):
    def _get_player(self, index=0):
        user = User.objects.get_or_create(username='testuser%d' % index)[0]
        user.set_password('test')
        user.save()
        return user.get_profile()