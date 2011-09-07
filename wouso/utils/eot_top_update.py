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

    from wouso.core.user.models import UserProfile
    from wouso.interface.top.models import TopUser, History

    today = date.today()
    print 'Updating with date: ', today
    for i,u in enumerate(UserProfile.objects.all().order_by('-points')):
        topuser = u.get_extension(TopUser)
        position = i + 1
        hs, new = History.objects.get_or_create(user=topuser,
                                            date=today)
        hs.position, hs.points = position, u.points
        hs.save()

    print 'Done.'

if __name__ == '__main__':
    main()
