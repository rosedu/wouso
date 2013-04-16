import json
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.conf import settings
from wouso.core.magic.models import Spell, ArtifactGroup
from wouso.core.scoring.models import Formula, Coin
from wouso.core.tests import WousoTest


class DisableAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('test')
        self.user.save()
        self.client.login(username='test', password='test')

    def test_enabled(self):
        settings.API_ENABLED = True
        response = self.client.get('/request_token')
        self.assertTrue(response.status_code, 200)

    def test_disabled(self):
        settings.API_ENABLED = False
        response = self.client.get('/request_token')
        self.assertTrue(response.status_code, 404)


class BazaarApi(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('_test', '', password='test')
        self.client.login(username='_test', password='test')

    def test_bazaar_buy_no_get(self):
        response = self.client.get('/api/bazaar/buy/')

        self.assertEqual(response.status_code, 405)

    def test_bazaar_buy_no_spell(self):
        response = self.client.post('/api/bazaar/buy/', {'spell': -1})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertFalse(data['success'])

    def test_bazaar_buy_ok(self):
        spell = Spell.objects.create(price=0)
        f = Formula.add('buy-spell')
        f.definition = 'points=0'
        f.save()
        Coin.add('points')

        response = self.client.post('/api/bazaar/buy/', {'spell': spell.id})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertTrue(data['success'])

        player = self.user.get_profile()

        self.assertTrue(spell in [s.spell for s in player.magic.spells_available])


class NotificationRegister(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('_test', '', password='test')
        self.client.login(username='_test', password='test')

    def test_notification_register_fail(self):
        response = self.client.post('/api/notifications/register/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'No registration_id provided')


    def test_notification_register_ok(self):
        response = self.client.post('/api/notifications/register/', {'registration_id': '1245'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)


class CastSpell(WousoTest):
    def test_cast(self):
        u1 = self._get_player()
        u2 = self._get_player(2)
        s = Spell.objects.create(due_days=0)
        u1.magic.add_spell(s)

        self.client.login(username=u1.user.username, password='test')

        response = self.client.post('/api/player/{id}/cast/'.format(id=u2.id), {'spell': s.id})

        data = json.loads(response.content)
        self.assertEqual(data['success'], True)