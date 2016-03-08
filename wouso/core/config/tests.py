from django.test import TestCase
from django.core.cache import cache
from models import Setting, BoolSetting, HTMLSetting, ChoicesSetting


class TestSettings(TestCase):
    def setUp(self):
        cache.clear()

    def test_setting_type(self):
        a = BoolSetting.get('test-name')  # automatically created

        self.assertTrue(a)
        self.assertIsInstance(a, Setting)
        self.assertIsInstance(a, BoolSetting)

        self.assertEqual(type(a.get_value()), bool)

        b = HTMLSetting.get('test2')
        self.assertIsInstance(b, HTMLSetting)

        c = ChoicesSetting.get('test3')
        self.assertIsInstance(c, ChoicesSetting)

    def test_set_value(self):
        a = BoolSetting.get('test')

        a.set_value(False)
        self.assertEqual(a.get_value(), False)
        self.assertIsInstance(a.get_value(), bool)

    def test_setting_forms(self):
        c = ChoicesSetting.get('test')

        self.assertTrue('<select' in c.form())

        h = HTMLSetting.get('test')
        self.assertTrue('<textarea' in h.form())

        b = BoolSetting.get('test')
        self.assertTrue('checkbox' in b.form())

        c.choices = zip(range(3), range(3))
        self.assertTrue('value="0"' in c.form())

    def test_setting_unicode(self):
        a = Setting.get('test')

        self.assertEqual(a.__unicode__(), 'test')

        a.set_value('e')
        self.assertEqual(a.get_value(), 'e')
