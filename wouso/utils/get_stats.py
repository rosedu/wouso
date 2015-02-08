#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/get_stats.py

import sys
import csv
import os
import wouso.utils.user_util

# Setup Django environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from django.contrib.auth.models import User
from wouso.core.user.models import Race
from wouso.core.user.models import Player

def main():
    ulist = User.objects.all()
    accounts_per_race_dict = {}
    for u in ulist:
        p = Player.objects.get(user__username=u.username)
        if not p:
            print "Player account for username %s not found." %(u.username)
            continue
        if not p.race:  # Player with no race (such as admin).
            continue

        if p.race.name in accounts_per_race_dict:
            accounts_per_race_dict[p.race.name] += 1
        else:
            accounts_per_race_dict[p.race.name] = 1

    for race, num in accounts_per_race_dict.iteritems():
        r = Race.objects.get(name=race)
        print "%s, %s, %d" %(r.name, r.title, num)
    print "Total: %d" %(ulist.count())

if __name__ == "__main__":
    sys.exit(main())
