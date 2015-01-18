#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/add_races.py utils/sample-data/sample-race-list.csv

import sys
import csv
import wouso.utils.user_util

def main():
    if len(sys.argv) != 2:
        print 'Usage: python add_races.py <file.csv>'
        print " CSV columns: race_name race_title"
        sys.exit(1)

    csvfile = open(sys.argv[1], 'r')
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        race_name, race_title = row
        ret = wouso.utils.user_util.add_race(race_name, race_title)
        if ret:
            print "Successfully added race %s." %(race_name)
        else:
            print "Failed adding race %s." %(race_name)


if __name__ == "__main__":
    sys.exit(main())
