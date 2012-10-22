# coding=utf-8
# This has to be used from the wouso folder like so:
# PYTHONPATH=. python utils/import_questions

import sys
import csv
from django.core.management import setup_environ


def init():
    import settings
    setup_environ(settings)


def main():

    if len(sys.argv) != 2:
        print 'Usage: import_users.py <file.csv>'
        print " CSV columns: last name, first name, uid, group"
        sys.exit(1)

    try:
        init()
    except ImportError:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from django.contrib.auth.models import User
    from wouso.core.user.models import PlayerGroup, Player

    with open(sys.argv[1], 'r') as fin:
        reader = csv.reader(fin)
        for row in reader:
            last_name, first_name, username, group = row
            try:
                to_group = PlayerGroup.objects.get(name=group)
            except PlayerGroup.DoesNotExist:
                print u"Ignoring %s in group %s (group does not exist in db)" % (last_name, group)
                continue

            user, new = User.objects.get_or_create(username=username)
            if new:
                user.first_name = first_name
                user.last_name = last_name
                user.save()
            try:
                player = user.get_profile()
            except Player.DoesNotExist:
                print u"Error on %s: Player does not exist" % username
            else:
                player.race = to_group.parent
                player.save()
                player.set_group(to_group)
                print u"Added {player} to {group} ".format(player=player.user.username, group=to_group)

    print 'Done.'


if __name__ == '__main__':
    main()
