#!/usr/bin/env python
#
import sys
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

    from wouso.core.scoring import sync_all_user_points

    print 'Synchronizing user points with history:'
    sync_all_user_points()
    print 'Done.'

    return 0


if __name__ == '__main__':
    sys.exit(main())
