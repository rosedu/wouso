#!/usr/bin/env python
# End of the day top update script:
#   Preserve points and position for each user.
#   Call this in cron at 11:59 am.
#
import sys
import csv
from datetime import date, timedelta
from time import strftime
from django.core.management import setup_environ

def init():
    import settings
    setup_environ(settings)

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

def main(args):
    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from django.db import models
    from wouso.core.user.models import Player
    from wouso.core.scoring.models import History, Formula

    res = History.objects.aggregate(models.Min('timestamp'))['timestamp__min']
    start_date = res.date() if res else date.today()
    end_date = date.today()
        
    data = []
    print "Analyzing ", start_date, "-", end_date
    for single_date in daterange(start_date, end_date):
        #print strftime("%Y-%m-%d", single_date.timetuple())
        print '.'

        singledata = {'date': single_date, 'data': []}
        for player in Player.objects.all():
            hs = History.objects.filter(timestamp__year=single_date.year, timestamp__month=single_date.month, timestamp__day=single_date.day, user=player)
            
            player = {'uid': player.pk}
            has_score = False
            for formula in Formula.objects.all():
                hss = hs.filter(formula=formula).aggregate(models.Sum('amount'))['amount__sum']
                if hss:
                    player[formula.id] = hss
                    has_score = True
                    #print formula.id, hss
                else:
                    player[formula.id] = 0
     
            if has_score:
                singledata['data'].append(player)
        
        if singledata['data']:    
            data.append(singledata)
    # final
    writer = csv.writer(open('statistics.csv', 'w'))
    row = ['date', 'user'] + [f.id for f in Formula.objects.all()]
    writer.writerow(row)
    for d in data:
        for p in d['data']:
            row = ["%s" % d['date'], "%d" % p['uid']]
            for formula in Formula.objects.all():
                row.append("%d" % p.get(formula.id, 0))
            writer.writerow(row)
    print " done!"

if __name__ == '__main__':
    main(sys.argv)
