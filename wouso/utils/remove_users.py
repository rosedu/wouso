#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/remove_users.py users.txt

import sys
import csv
import wouso.utils.user_util

def main():
    if len(sys.argv) != 2:
        print 'Usage: python remove_users.py <input-file>'
        print " Input file contains usernames, one per line."
        sys.exit(1)

    for line in open(sys.argv[1], 'r'):
        username = line.strip()
        try:
            ret = wouso.utils.user_util.remove_user(username)
        except Exception, e:
            print "Failed removing user %s." %(username)
        else:
            if ret:
                print "Successfully removed user %s." %(username)
            else:
                print "Failed removing user %s." %(username)


if __name__ == "__main__":
    sys.exit(main())
