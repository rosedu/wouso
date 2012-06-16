import json
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from wouso.core.magic.models import Spell, Group
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
        group = Group.objects.create(name='spells')
        spell = Spell.objects.create(price=0, group=group)
        Formula.objects.create(id='buy-spell', formula='points=0')
        Coin.objects.create(id='points')

        response = self.client.post('/api/bazaar/buy/', {'spell': spell.id})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertTrue(data['success'])

        player = self.user.get_profile()

        self.assertTrue(spell in [s.spell for s in player.spells_available])