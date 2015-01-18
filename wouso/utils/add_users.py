#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/add_users.py utils/sample-data/sample-user-list.csv

import sys
import csv
import wouso.utils.user_util

def main():
    if len(sys.argv) != 2:
        print 'Usage: python add_users.py <file.csv>'
        print " CSV columns: username, first name, last name, email, password"
        sys.exit(1)

    csvfile = open(sys.argv[1], 'r')
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        username, first_name, last_name, email, password = row
        ret = wouso.utils.user_util.add_user(username, first_name, last_name, email, password, is_active=1, is_staff=0, is_superuser=0)
        if ret:
            print "Successfully added user %s." %(username)
        else:
            print "Failed adding user %s." %(username)


if __name__ == "__main__":
    sys.exit(main())
