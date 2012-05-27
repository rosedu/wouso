#!/usr/bin/env python
# End of the day top update script:
#   Preserve points and position for each user.
#   Call this in cron at 11:59 am.
#
import sys
from datetime import date
from django.core.management import setup_environ
from wouso.core.magic.models import SpellHistory

def init():
    import settings
    setup_environ(settings)

def main(args):
    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from wouso.core.user.models import Player, PlayerGroup
    from wouso.interface.top.models import TopUser, History

    today = date.today()
    print 'Updating users with date: ', today
    for i,u in enumerate(Player.objects.all().order_by('-points')):
        topuser = u.get_extension(TopUser)
        position = i + 1
        hs, new = History.objects.get_or_create(user=topuser, date=today, relative_to=None)
        hs.position, hs.points = position, u.points
        hs.save()

    print 'Updating group history: '
    for p in PlayerGroup.objects.all():
        p.points = p.live_points
        p.save()
    # get position on distinct classes
    for cls in PlayerGroup.objects.values_list('gclass').distinct():
        cls = cls[0]
        for i,p in enumerate(PlayerGroup.objects.filter(gclass=cls).order_by('-points')):
            position = i + 1
            hs, new = History.objects.get_or_create(group=p, date=today, relative_to=None)
            hs.position, hs.points = position, p.points
            hs.save()
    print 'Updating user relative to group position: '
    for g in PlayerGroup.objects.all():
        for i,u in enumerate(g.player_set.order_by('-points')):
            topuser = u.get_extension(TopUser)
            position = i + 1
            hs, new = History.objects.get_or_create(user=topuser, date=today, relative_to=g)
            hs.position, hs.points = position, p.points
            hs.save()
    print 'Updating group relative to parent group position: '
    for g in PlayerGroup.objects.all():
        if g.children:
            for i,c in enumerate(g.children.order_by('-points')):
                position = i + 1
                hs, new = History.objects.get_or_create(group=c, date=today, relative_to=g)
                hs.position, hs.points = position, p.points
                hs.save()

    from wouso.games.challenge.models import Challenge
    
    challenges = Challenge.get_expired(today)
    print 'Updating expired challenges ', len(challenges)
    for c in challenges:
        if c.is_launched():
            # launched before yesterday, automatically refuse
            c.refuse(auto=True)
        else:
            # launched and accepted before yesterday, but not played by both
            c.set_expired()

    from wouso.core.user.models import PlayerSpellDue

    spells = PlayerSpellDue.get_expired(today)
    print 'Updating expired spells (%d)' % spells.count()
    for s in spells:
        SpellHistory.expired(s.player, s.spell)
        s.delete()

    print 'Done.'

if __name__ == '__main__':
    main(sys.argv)
