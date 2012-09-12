from django.contrib.auth.models import User
from django.test import TestCase

class WousoTest(TestCase):
    def _get_player(self, index=0):
        user = User.objects.create(username='testuser%d' % index)
        user.set_password('test')
        user.save()
        return user.get_profile()