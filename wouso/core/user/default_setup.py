import sys
sys.path.append('..');sys.path.append('.')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import Group, Permission
from wouso.core.user.models import PlayerGroup, Race

if __name__ == '__main__':
    print 'Setting up groups...',
    series = ('CA', 'CB', 'CC', 'Others')
    groups = range(311, 316)
    for i in series:
        pg,nw = Race.objects.get_or_create(name=i)
        if i == 'Others':
            pg.show_in_top = False
            pg.save()
            continue
        for j in groups:
            name = i + '' + str(j)
            gg,nw = Group.objects.get_or_create(name=name)
            pgg,nw = PlayerGroup.objects.get_or_create(group=gg,parent=pg,name=name)
    print 'done!'

    # Assistants group, 'Staff'
    staff, new = Group.objects.get_or_create(name='Staff')
    cpanel_perm = Permission.objects.get(codename='change_setting')
    staff.permissions.add(cpanel_perm)

    # Dump
    print "Groups: "
    for c in PlayerGroup.objects.all():
        print " ", c
