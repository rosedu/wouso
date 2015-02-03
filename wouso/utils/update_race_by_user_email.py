#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/update_race_by_user_email.py emails.txt new_race

import sys
import csv
import os
import wouso.utils.user_util

# Setup Django environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from django.contrib.auth.models import User

def main():
    if len(sys.argv) != 3:
        print 'Usage: python add_users.py <list-of-emails.txt> <new-race>'
        sys.exit(1)

    print "number of users: %d" %(User.objects.all().count())
    for line in open(sys.argv[1], 'r'):
        email = line.strip()
        print "email: %s" %(email)
        try:
            u = User.objects.get(email=email)
        except:
            print "No user with email address %s." %(email)
            continue
        if not u:
            print "No user with email address %s." %(email)
            continue
        wouso.utils.user_util.add_user_to_race(u.username, sys.argv[2])
        print "Updated race for user %s (%s) to %s." %(u.username, email, sys.argv[2])

if __name__ == "__main__":
    sys.exit(main())
