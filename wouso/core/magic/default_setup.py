import sys
sys.path.append('..')
sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from wouso.core import magic
from wouso.core.magic.models import *
from wouso.core.user.models import Player


if __name__ == '__main__':
    print 'Setting up the Artifacts...',

    # Spell group
    spell_group, new = ArtifactGroup.objects.get_or_create(name='Spells')

    # Group groups
    ca, new = ArtifactGroup.objects.get_or_create(name='CA')
    cb, new = ArtifactGroup.objects.get_or_create(name='CB')
    cc, new = ArtifactGroup.objects.get_or_create(name='CC')

    # Create a default group
    default_group, new = ArtifactGroup.objects.get_or_create(name='Default')
    for i in range(7):
        name = 'level-%d' % (i + 1)
        title = 'Level %d' % (i + 1)
        for g in (default_group, ca, cb, cc):
            Artifact.objects.get_or_create(
                name=name,
                group=g,
                title=title)

    print "done"
    # Assure each user has a level
    #level = Artifact.get_level_1()
    #for u in Player.objects.all():
    #    if u.level is None:
    #        u.level = level
    #        u.save()

    # Dump
    print "Groups: "
    for c in ArtifactGroup.objects.all():
        print " ", c
    print "Artifacts: "
    for f in Artifact.objects.all():
        print " ", f, f.title
