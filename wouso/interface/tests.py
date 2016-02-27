from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from wouso.core.tests import WousoTest
from bs4 import BeautifulSoup

class TestInterface(WousoTest):
    def test_homepage_anonymous(self):
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_homepage_player(self):
        player = self._get_player()
        self.client.login(username=player.user.username, password='test')
        response = self.client.get('/hub/')

        self.assertTrue('Logout' in response.content)

    def test_online_player(self):
        player = self._get_player()
        self.client.login(username=player.user.username, password='test')
        response = self.client.get('/hub/')
        soup = BeautifulSoup(response.content, "html.parser")
        last10_div = soup.find_all(class_="widget")[0]

        self.assertTrue(player.user.username in str(last10_div))

    def test_profile_page(self):
        admin = self._get_superuser()
        self._client_superuser()
        response = self.client.get(reverse('player_profile', kwargs=dict(id=admin.id)))
        self.assertEqual(response.status_code, 200)

    def test_admin_has_control_panel_button(self):
        admin = self._get_superuser()
        self._client_superuser()
        response = self.client.get('/hub/')

        soup = BeautifulSoup(response.content, "html.parser")
        button = soup.find_all(id="head-cpanel")
        self.assertEqual(len(button), 1)

    def test_user_has_no_control_panel_button(self):
        player = self._get_player()
        self.client.login(username=player.user.username, password='test')
        response = self.client.get('/hub')
        soup  = BeautifulSoup(response.content, "html.parser")
        button = soup.find_all(id="head-cpanel")
        self.assertEqual(len(button), 0)