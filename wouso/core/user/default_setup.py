import sys
sys.path.append('..');sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import Group
from wouso.core.user.models import PlayerGroup

if __name__ == '__main__':
    print 'Setting up groups...',
    series = ('CA', 'CB', 'CC', 'Others')
    groups = range(311, 316)
    for i in series:
        g,nw = Group.objects.get_or_create(name=i)
        pg,nw = PlayerGroup.objects.get_or_create(group=g,name=i,gclass=1)
        if i == 'Others':
            continue
        for j in groups:
            name = i + '' + str(j)
            gg,nw = Group.objects.get_or_create(name=name)
            pgg,nw = PlayerGroup.objects.get_or_create(group=gg,parent=pg,name=name)
    print 'done!'

    # Dump
    print "Groups: "
    for c in PlayerGroup.objects.all():
        print " ", c
