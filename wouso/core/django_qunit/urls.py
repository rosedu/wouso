from django.conf.urls.defaults import *
from django.conf import settings
import os

media_root = os.path.join(os.path.dirname(__file__), 'media')

urlpatterns = patterns('',
    url(r'^tests/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.QUNIT_TEST_DIRECTORY,
    }, name='qunit_test'),
    url(r'^qunit/qunit.js', 'django.views.static.serve', {
        'document_root': media_root, 'path': 'qunit/qunit.js',
    }, name='qunit_js'),
    url(r'^qunit/qunit.css', 'django.views.static.serve', {
        'document_root': media_root, 'path': 'qunit/qunit.css',
    }, name='qunit_css'),
    url('^(?P<path>.*)$', 'django_qunit.views.run_tests',
        name='qunit_test_overview'),
)
