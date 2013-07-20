from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from wouso.core.scoring.models import Formula
from wouso.core.tests import WousoTest

class addPlayerTestCase(TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test1', is_staff=True, is_superuser=True)
        self.user.set_password('secret')
        self.user.save()

    def test_add_user(self):
        old_number = len(User.objects.all())
        self.client = Client()
        self.client.login(username='_test1', password='secret')
        User.objects.get(pk=1).is_staff
        resp = self.client.post('/cpanel/add_player/', {'username': '_test2', 'password': 'secret'})
        new_number = len(User.objects.all())

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(old_number + 1, new_number)

class CpanelViewsTest(WousoTest):
    def setUp(self):
        super(CpanelViewsTest, self).setUp()
        self.admin = self._get_superuser()
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def test_edit_formula_view_get(self):
        formula = Formula.objects.create(name='test_formula1', definition='points=1234',
                                         description='First formula of the game')
        response = self.client.get(reverse('edit_formula', args=[formula.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="test_formula1"')
        self.assertContains(response, 'value="points=1234"')
        self.assertContains(response, 'First formula of the game')
