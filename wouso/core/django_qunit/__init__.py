from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    settings.QUNIT_TEST_DIRECTORY
except AttributeError:
    raise ImproperlyConfigured('Missing required setting QUNIT_TEST_DIRECTORY.')
