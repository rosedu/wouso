from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from wouso.core.tests import WousoTest

class TestInterface(WousoTest):
    def test_homepage_anonymous(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_homepage_player(self):
        player = self._get_player()
        self.client.login(username=player.user.username, password='test')
        response = self.client.get('/hub/')

        self.assertTrue('Logout' in response.content)

    def test_profile_page(self):
        admin = self._get_superuser()
        self._client_superuser()
        response = self.client.get(reverse('player_profile', kwargs=dict(id=admin.id)))
        self.assertEqual(response.status_code, 200)

    # def test_special_challenges(self):
    #     player = self._get_player()
    #     self.client.login(username=player.user.username, password='test')

    #     response = self.client.get('/hub/')

    #     self.assertTrue('Challenges' in response.content)

    # def test_messages_button(self):
    #     player = self._get_player()
    #     self.client.login(username=player.user.username, password='test')

    #     response = self.client.get('/hub/')

    #     self.assertTrue('Messages' in response.content)

    # def test_magic_button(self):
    #     player = self._get_player()
    #     self.client.login(username=player.user.username, password='test')

    #     response = self.client.get('/hub/')

    #     self.assertTrue('Magic' in response.content)

    # def test_special_button(self):
    #     player = self._get_player()
    #     self.client.login(username=player.user.username, password='test')

    #     response = self.client.get('/hub/')

    #     self.assertTrue('Special' in response.content)
    