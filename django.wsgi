import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'wouso.settings'

sys.path.append(os.path.normpath(os.path.dirname(__file__)))
sys.path.append(os.path.normpath(os.path.dirname(__file__))+'/wouso')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

