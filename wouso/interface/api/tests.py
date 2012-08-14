import json
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from wouso.core.magic.models import Spell, ArtifactGroup
from wouso.core.scoring.models import Formula, Coin

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
        group = ArtifactGroup.objects.create(name='spells')
        spell = Spell.objects.create(price=0, group=group)
        f = Formula.objects.get_or_create(id='buy-spell')[0]
        f.formula='points=0'
        f.save()
        Coin.objects.get_or_create(id='points')

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