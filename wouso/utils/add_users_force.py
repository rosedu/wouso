#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/add_users_force.py utils/sample-data/sample-user-list.csv

import sys
import csv
import wouso.utils.user_util

OP_SUCCESS = 0
OP_EXCEPTION = -1
OP_EXISTS = -2

def try_using_index_no_recurse(username, first_name, last_name, email, password):
    ret = OP_EXISTS
    for i in range(1,100):
        _username = username+"%d" %(i)
        ret = add_user_helper(_username, first_name, last_name, email, password)
        if ret == OP_SUCCESS:
            return (_username, ret)
        if ret == OP_EXCEPTION:
            wouso.utils.user_util.remove_user(_username)
            return (_username, ret)
    return (_username, ret)

def truncate_username(username):
    parts = username.split('.')
    if len(parts) != 2:
        print >>sys.stderr, "Username %s should consist of two parts."
        return
    return parts[0][0:1]+parts[1]

def try_using_truncate_no_recurse(username, first_name, last_name, email, password):
    username = truncate_username(username)
    return (username, add_user_helper(username, first_name, last_name, email, password))

def try_using_cookie_no_recurse(username, first_name, last_name, email, password, cookie):
    username = username+cookie
    return (username, add_user_helper(username, first_name, last_name, email, password))

def try_using_truncate(username, first_name, last_name, email, password, cookie):
    (username, ret) = try_using_truncate_no_recurse(username, first_name, last_name, email, password)

    if ret == OP_SUCCESS:
        return (username, True)

    if ret == OP_EXCEPTION:
        # If exception after truncation, abort.
        wouso.utils.user_util.remove_user(username)
        return (username, False)

    if ret == OP_EXISTS:
        # First try adding cookie.
        (new_username, ret) = try_using_cookie_no_recurse(username, first_name, last_name, email, password, cookie)
        if ret == OP_SUCCESS:
            return (new_username, True)
        if ret == OP_EXISTS:
            # Use index.
            username = new_username
            (username, ret) = try_using_index_no_recurse(username, first_name, last_name, email, password)
            if ret == OP_SUCCESS:
                return (username, True)
            if ret == OP_EXCEPTION:
                wouso.utils.user_util.remove_user(username)
            return (username, False)
        if ret == OP_EXCEPTION:
            # Try using truncate + index (no cookie).
            wouso.utils.user_util.remove_user(username)
            (username, ret) = try_using_index_no_recurse(username, first_name, last_name, email, password)
            if ret == OP_SUCCESS:
                return (username, True)
            if ret == OP_EXCEPTION:
                wouso.utils.user_util.remove_user(username)
            return (username, False)

    return (None, False)


def try_using_cookie(username, first_name, last_name, email, password, cookie):
    (username, ret) = try_using_cookie_no_recurse(username, first_name, last_name, email, password, cookie)

    if ret == OP_SUCCESS:
        return (username, True)

    if ret == OP_EXISTS:
        (new_username, ret) = try_using_index_no_recurse(username, first_name, last_name, email, password)
        if ret == OP_SUCCESS:
            return (new_username, ret)
        if ret == OP_EXISTS:
            # If it still exists, we need to abort.
            return (username, False)
        if ret == OP_EXCEPTION:
            wouso.utils.user_util.remove_user(new_username)
            # If length exception, truncate.
            (username, ret) = try_using_truncate_no_recurse(username, first_name, last_name, email, password)
            if ret == OP_SUCCESS:
                return (username, True)
            if ret == OP_EXCEPTION:
                wouso.utils.user_util.remove_user(username)
                return (username, False)
            if ret == OP_EXISTS:
                (username, ret) = try_using_index_no_recurse(username, first_name, last_name, email, password)
                if ret == OP_SUCCESS:
                    return (username, True)
                if ret == OP_EXCEPTION:
                    wouso.utils.user_util.remove_user(username)
                # Abort if unable to create username.
                return (username, False)

    if ret == OP_EXCEPTION:
        wouso.utils.user_util.remove_user(username)
        (username, ret) = try_using_truncate_no_recurse(username, first_name, last_name, email, password)
        if ret == OP_SUCCESS:
            return (username, True)
        if ret == OP_EXCEPTION:
            # Abort if exception still occurs.
            wouso.utils.user_util.remove_user(username)
            return (username, False)
        if ret == OP_EXISTS:
            (username, ret) = try_using_index_no_recurse(username, first_name, last_name, email, password)
            if ret == OP_SUCCESS:
                return (username, True)
            if ret == OP_EXCEPTION:
                wouso.utils.user_util.remove_user(username)
            # Abort if unable to create username.
            return (username, False)

    return (None, False)


def add_user_helper(username, first_name, last_name, email, password):
    """Helper function for adding user. Return value states wether operation
    completed successfully, and exception was encountered or use already
    existed.
    """
    try:
        ret = wouso.utils.user_util.add_user(username, first_name, last_name, email, password, is_active=1, is_staff=0, is_superuser=0)
    except Exception, e:
        print "h: Exception when adding %s." %(username)
        return OP_EXCEPTION
    if ret:
        print "h: Successfully added user %s." %(username)
        return OP_SUCCESS
    else:
        print "h: Failed adding user %s. User already exists." %(username)
    return OP_EXISTS


def add_user_no_matter_what(username, first_name, last_name, email, password, cookie):
    _ret = add_user_helper(username, first_name, last_name, email, password)

    # Assume everything went OK.
    ret = True

    # If username exists, first try adding cookie. Then add index. Maybe
    # truncate.
    if _ret == OP_EXISTS:
        (username, ret) = try_using_cookie(username, first_name, last_name, email, password, cookie)

    # If username is too large, truncate username. Then add cookie. Maybe
    # add index.
    elif _ret == OP_EXCEPTION:
        wouso.utils.user_util.remove_user(username)
        (username, ret) = try_using_truncate(username, first_name, last_name, email, password, cookie)

    return (username, ret)


def main():
    if len(sys.argv) != 2:
        print 'Usage: python add_users.py <file.csv>'
        print " CSV columns: username, first name, last name, email, password, cookie"
        sys.exit(1)

    csvfile = open(sys.argv[1], 'r')
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        username, first_name, last_name, email, password, cookie = row
        (_username, ret) = add_user_no_matter_what(username, first_name, last_name, email, password, cookie)
        if ret:
            print "Successfully added user %s." %(_username)
        if not ret:
            print "Failed adding user %s. Nothing worked." %(username)


if __name__ == "__main__":
    sys.exit(main())
