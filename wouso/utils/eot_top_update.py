#!/usr/bin/env python
# End of the day top update script:
#   Preserve points and position for each user.
#   Call this in cron at 11:59 am.
#
import sys
from datetime import date
from django.core.management import setup_environ

def init():
    import settings
    setup_environ(settings)

def main():
    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from wouso.core.user.models import Player, PlayerGroup
    from wouso.interface.top.models import TopUser, History

    today = date.today()
    print 'Updating users with date: ', today
    for i,u in enumerate(Player.objects.all().order_by('-points')):
        topuser = u.get_extension(TopUser)
        position = i + 1
        hs, new = History.objects.get_or_create(user=topuser, date=today)
        hs.position, hs.points = position, u.points
        hs.save()

    print 'Updating group history: '
    for p in PlayerGroup.objects.all():
        p.points = p.live_points
        p.save()
    for i,p in enumerate(PlayerGroup.objects.all().order_by('-points')):
        position = i + 1
        hs, new = History.objects.get_or_create(group=p, date=today)
        hs.position, hs.points = position, p.points
        hs.save()

    print 'Done.'

if __name__ == '__main__':
    main()
