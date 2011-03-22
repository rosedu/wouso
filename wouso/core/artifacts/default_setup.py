import sys
sys.path.append('..');sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from wouso.core import artifacts
from wouso.core.artifacts.models import *

if __name__ == '__main__':
    print 'Setting up the Artifacts...',
    
    # Create a default group
    default_group, new = Group.objects.get_or_create(name='Default')
    for i in range(7):
        name='level-%d' % (i + 1)
        title='Level %d' % (i + 1)
        Artifact.objects.get_or_create(
            name=name,
            group=default_group,
            title=title)
    
    print "done"
    
    # Dump
    print "Groups: "
    for c in Group.objects.all():
        print " ", c
    print "Artifacts: "
    for f in Artifact.objects.all():
        print " ", f, f.title
