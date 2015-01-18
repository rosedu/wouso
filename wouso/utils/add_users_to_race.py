#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/add_users_to_race.py utils/sample-data/sample-user-race-mapping.csv

import sys
import csv
import wouso.utils.user_util

def main():
    if len(sys.argv) != 2:
        print 'Usage: python add_users_to_race.py <file.csv>'
        print " CSV columns: username race_name"
        sys.exit(1)

    csvfile = open(sys.argv[1], 'r')
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        username, race_name = row
        ret = wouso.utils.user_util.add_user_to_race(username, race_name)
        if ret:
            print "Successfully added %s to race %s." %(username, race_name)
        else:
            print "Failed adding %s to race %s." %(username, race_name)


if __name__ == "__main__":
    sys.exit(main())
