# Django settings for wouso project.
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'wouso',
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'root',
        'PASSWORD': 'alex',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Bucharest'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.normpath(os.path.dirname(__file__) + "/static/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6%8q5z_+rml3oh*7v2sspp7fgdadueh+#$r+d%l__5sg07j3f7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# List of callables that will get template data, if needed
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth', 
    'django.core.context_processors.debug', 
    'django.core.context_processors.i18n', 
    'django.core.context_processors.media', 
    'django.core.context_processors.request', 
    'wouso.context.config',
    'wouso.context.games_info',
    'wouso.context.userprofile',
    'wouso.context.top10',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'facebook.djangofb.FacebookMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'facebookconnect.middleware.FacebookConnectMiddleware'
)
AUTHENTICATION_BACKENDS = (
    'facebookconnect.models.FacebookBackend',
    'wouso.connections.ldap_backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'wouso.urls'

TEMPLATE_DIRS = (
    os.path.normpath(os.path.dirname(__file__) + "/templates/"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.admin',
    'wouso.games.qotd',
    'wouso.core.profile',
    'wouso.games.challenge',
    'wouso.games.wquest',
    'wouso.extra.activity',
    #'wouso.core.profile.templatetags.profile_tags',
    'facebookconnect'
)

LOGIN_REDIRECT_URL = '/user/profile/'
LOGIN_URL = '/user/login/'
AUTH_PROFILE_MODULE = 'profile.UserProfile'

# For profile's artifacts
MEDIA_ARTIFACTS = "artifacts/"

# Facebook
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''
FACEBOOK_INTERNAL = True

# Local settings
if os.path.isfile(os.path.dirname(__file__) + "/localsettings.py"):
    from localsettings import *
