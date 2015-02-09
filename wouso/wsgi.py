import os, sys

# Add wouso folder and parent folder to path.
sys.path.append(os.path.normpath(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.normpath(os.path.dirname(__file__)),".."))

# Poiting to the project settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
