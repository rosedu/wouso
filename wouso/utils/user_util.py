#!/usr/bin/env/python

# To test, run from parent folder using
#    PYTHONPATH=. python utils/user_util.py.

from django.core.management import setup_environ

def main():
    import settings
    setup_environ(settings)

import sys

if __name__ == "__main__":
    sys.exit(main())

from django.contrib.auth.models import User
from wouso.core.user.models import Race
from wouso.core.user.models import Player

def add_user(username, first_name, last_name, email, password, is_active=False, is_staff=False, is_superuser=False):
    """Add user and return user object. In case user with given username
    already exists, return None.
    """
    user, new = User.objects.get_or_create(username=username)
    if not new:
        return None

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.set_password = password
    user.is_active = is_active
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user

def remove_user(username):
    """Remove user by username. Return True if successful. Return False if user
    does not exist.
    """
    user = User.objects.get(username=username)
    if not user:
        return False

    user.delete()
    return True

def update_user(username, first_name=None, last_name=None, email=None, password=None, is_active=None, is_staff=None, is_superuser=None):
    """Update user by username. Return True if successful. Return False if user
    does not exist.
    """
    user = User.objects.get(username=username)
    if not user:
        return False

    if first_name != None:
        user.first_name = first_name
    if last_name != None:
        user.last_name = last_name
    if email != None:
        user.email = email
    if password != None:
        user.set_password = password
    if is_active != None:
        user.is_active = is_active
    if is_staff != None:
        user.is_staff = is_staff
    if is_superuser != None:
        user.is_superuser = is_superuser
    user.save()
    return True

def change_password(username, password):
    """Change user password. Return True on success. Return False if user does
    not exist.
    """
    return update_user(username, password=password)

def add_race(name, title, can_play=False):
    """Add race and return race object. In case race already exists, return
    None.
    """
    race, new = Race.objects.get_or_create(name=name)
    if not new:
        return None

    race.title = title
    race.can_play = can_play
    race.save()
    return race

def remove_race(name):
    """Remove race by name. Return True if successful. Return False if race
    does not exist.
    """
    race = Race.objects.get(name=name)
    if not race:
        return False

    race.delete()
    return True

def update_race(name, title=None, can_play=None):
    """Update user by username. Return True if successful. Return False if user
    does not exist.
    """
    race = Race.objects.get(name=name)
    if not race:
        return False

    if title != None:
        race.title = title
    if can_play != None:
        race.can_play = can_play
    race.save()
    return True

def add_user_to_race(username, race_name):
    """Add user to race. Return True if successful. Return False if user or
    race does not exist."""
    user = User.objects.get(username=username)
    if not user:
        return False
    race = Race.objects.get(name=race_name)
    if not race:
        return False

    try:
        player = user.get_profile()
    except Player.DoesNotExist:
        return False
    player.race = race
    player.save()
    return True

def remove_user_from_race(username, race_name):
    """Add user to race. Return True if successful. Return False if user or
    race does not exist. Race is actually non important. It will simply be set
    to None."""
    user = User.objects.get(username=username)
    if not user:
        return False
    race = Race.objects.get(name=name)
    if not race:
        return False

    try:
        player = user.get_profile()
    except Player.DoesNotExist:
        return False
    player.race = None
    player.save()
    return True

