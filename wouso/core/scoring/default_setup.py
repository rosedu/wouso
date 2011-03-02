import sys
sys.path.append('..');sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from wouso.core import scoring

if __name__ == '__main__':
    print 'Setting up the Scoring module...',
    scoring.setup()
    print 'done!'
