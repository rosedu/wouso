#!/usr/bin/env/python

# To test, run from parent folder using commands such as:
# PYTHONPATH=../:. python utils/user_util.py --list-users
# PYTHONPATH=../:. python utils/user_util.py --list-races
# PYTHONPATH=../:. python utils/user_util.py --show-user cristian.palianos
# PYTHONPATH=../:. python utils/user_util.py --show-race cn-unirea

import argparse
import sys
import os
import codecs

# Setup Django environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from django.contrib.auth.models import User
from wouso.core.user.models import Race
from wouso.core.user.models import Player

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

def _print_user(user):
    """Print information about an user.
    """
    print "%s,%s,%s,%s,%s,%s,%s" %(user.username, user.first_name, \
            user.last_name, user.email, user.is_active, user.is_staff, \
            user.is_superuser)

def _print_player(player):
    """Print information about a player. Same as user but add race name.
    """
    user = player.user
    race_name = player.race.name if player.race else "None"
    race_title = player.race.title if player.race else "None"
    print "%s,%s,%s,%s,%s,%s,%s,%s,%s" %(user.username, user.first_name, \
            user.last_name, user.email, user.is_active, user.is_staff, \
            user.is_superuser, race_name, race_title)

def _print_race(race):
    """Print information about a race.
    """
    print "%s,%s,%s" %(race.name, race.title, race.can_play)

def list_users(race=None):
    """List users belonging to a particular race. In case race is missing,
    list all users."""
    players = Player.objects.all()
    if race:
        users = []
        for p in players:
            if p.race == None:
                continue
            if p.race.name == race:
                users.append(p.user)
    else:
        users = [p.user for p in players]
    for u in users:
        _print_user(u)

def list_players(race=None):
    """List players belonging to a particular race. In case race is missing,
    list all players. Add printing of race name."""
    _players = Player.objects.all()
    if race:
        players = []
        for p in _players:
            if p.race == None:
                continue
            if p.race.name == race:
                players.append(p)
    else:
        players = _players
    for p in players:
        _print_player(p)

def list_races(race=None):
    """List all races.
    """
    for r in Race.objects.all():
        _print_race(r)

def show_user(username):
    """Show information of user.
    """
    p = Player.objects.get(user__username=username)
    if not p:
        return
    _print_user(p.user)
    print "race: %s, %s" %(p.race.name, p.race.title)

def show_race(race_name):
    """Show information about race.
    """
    r = Race.objects.get(name=race_name)
    if not r:
        return
    _print_race(r)

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
    user.set_password(password)
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
        user.set_password(password)
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
    player = Player.objects.get(user__username=username)
    if not player:
        return False
    race = Race.objects.get(name=race_name)
    if not race:
        return False

    player.race = race
    player.save()
    return True

def remove_user_from_race(username, race_name):
    """Remove user from race. Return True if successful. Return False if user
    or race does not exist. Race is actually non important. It will simply be
    set to None."""
    player = Player.objects.get(user__username=username)
    if not player:
        return False
    race = Race.objects.get(name=race_name)
    if not race:
        return False

    player.race = None
    player.save()
    return True


def main():
    """In main, parse command line arguments and call corresponding functions.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--list-users", help="list users (in race)", const='###', nargs='?', metavar="RACE")
    parser.add_argument("--list-players", help="list players (in race)", const='###', nargs='?', metavar="RACE")
    parser.add_argument("--list-races", help="list races", action="store_true")
    parser.add_argument("--show-user", help="show summary info about user", metavar="USERNAME")
    parser.add_argument("--show-race", help="show summary info about race", metavar="RACE_NAME")
    parser.add_argument("--add-user", help="add user", nargs=8, metavar=("USERNAME", "FIRST_NAME", "LAST_NAME", "EMAIL", "PASSWORD", "IS_ACTIVE", "IS_STAFF", "IS_SUPERUSER"))
    parser.add_argument("--add-race", help="add race", nargs=3, metavar=("RACE_NAME", "RACE_TITLE", "CAN_PLAY"))
    parser.add_argument("--update-user", help="update user", nargs=7, metavar=("USERNAME", "FIRST_NAME", "LAST_NAME", "EMAIL", "IS_ACTIVE", "IS_STAFF", "IS_SUPERUSER"))
    parser.add_argument("--update-race", help="update race", nargs=3, metavar=("RACE_NAME", "RACE_TITLE", "CAN_PLAY"))
    parser.add_argument("--remove-user", help="remove user", metavar="USERNAME")
    parser.add_argument("--remove-race", help="remove race", metavar="RACE_NAME")
    parser.add_argument("--change-password", help="change user password", nargs=2, metavar=("USERNAME", "PASSWORD"))
    parser.add_argument("--add-user-to-race", help="add user to race", nargs=2, metavar=("USERNAME", "RACE_NAME"))
    parser.add_argument("--remove-user-from-race", help="remove user from race", nargs=2, metavar=("USERNAME", "RACE_NAME"))
    args = parser.parse_args()

    if args.list_users:
        race = args.list_users
        if args.list_users == '###':
            race = None
        list_users(race)

    if args.list_players:
        race = args.list_players
        if args.list_players == '###':
            race = None
        list_players(race)

    if args.list_races:
        list_races()

    if args.show_user:
        show_user(args.show_user)

    if args.show_race:
        show_race(args.show_race)

    if args.add_user:
        username = args.add_user[0]
        first_name = args.add_user[1]
        last_name = args.add_user[2]
        email = args.add_user[3]
        password = args.add_user[4]
        is_active = (True if args.add_user[5] == '1' else False)
        is_staff = (True if args.add_user[6] == '1' else False)
        is_superuser = (True if args.add_user[7] == '1' else False)
        add_user(username, first_name, last_name, email, password, is_active, is_staff, is_superuser)

    if args.add_race:
        name = args.add_race[0]
        title = args.add_race[1]
        can_play = (True if args.add_race[2] == '1' else False)
        add_race(name, title, can_play)

    if args.update_user:
        username = args.update_user[0]
        first_name = args.update_user[1]
        last_name = args.update_user[2]
        email = args.update_user[3]
        is_active = (True if args.update_user[4] == '1' else False)
        is_staff = (True if args.update_user[5] == '1' else False)
        is_superuser = (True if args.update_user[6] == '1' else False)
        update_user(username, first_name, last_name, email, None, is_active, is_staff, is_superuser)

    if args.update_race:
        name = args.update_race[0]
        title = args.update_race[1]
        can_play = (True if args.update_race[2] == '1' else False)
        update_race(name, title, can_play)

    if args.remove_user:
        remove_user(args.remove_user)

    if args.remove_race:
        remove_race(args.remove_race)

    if args.change_password:
        username = args.change_password[0]
        password = args.change_password[1]
        change_password(username, password)

    if args.add_user_to_race:
        username = args.add_user_to_race[0]
        race_name = args.add_user_to_race[1]
        add_user_to_race(username, race_name)

    if args.remove_user_from_race:
        username = args.remove_user_from_race[0]
        race_name = args.remove_user_from_race[1]
        remove_user_from_race(username, race_name)


if __name__ == "__main__":
    sys.exit(main())
