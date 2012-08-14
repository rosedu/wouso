import sys
sys.path.append('..');sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from wouso.core import scoring
from wouso.core.scoring.models import *

if __name__ == '__main__':
    print 'Setting up the Scoring module...',
    # TODO: i'm pretty sure this can be accomplished by simple fixtures.
    scoring.setup_scoring()
    print 'done!'

    # Dump
    print "Coins: "
    for c in Coin.objects.all():
        print " ", c
    print "Formulas: "
    for f in Formula.objects.all():
        print " ", f
