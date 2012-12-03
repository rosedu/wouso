#!/usr/bin/env python
# End of the day top update script:
#   Preserve points and position for each user.
#   Call this in cron at 11:59 am.
#
import argparse
import sys
import csv
from datetime import date, timedelta
from django.core.management import setup_environ


def init():
    import settings
    setup_environ(settings)


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)


def save_csv(csv_path, data):
    with open(csv_path, 'w') as fout:
        writer = csv.writer(fout)
        for row in data:
            writer.writerow(row)

    return csv_path


def scoring_activity_stats():
    from wouso.core.user.models import Player
    from wouso.core.scoring.models import History

    data = []
    header = ['id',
              'player',
              'days',
              'days_positive'
    ]
    data.append(header)
    for p in Player.objects.all():
        day = None
        days = 0
        days_positive = 0
        hs = History.objects.filter(user=p.user).order_by('timestamp')
        for h in hs:
            if h.timestamp.date() != day:
                days += 1
                day = h.timestamp.date()
        day = None
        for h in hs.filter(amount__gt=0):
            if h.timestamp.date() != day:
                days_positive += 1
                day = h.timestamp.date()
        data.append([p.id, p, days, days_positive])
    return data


def peruser_stats():
    from wouso.core.user.models import Player
    from wouso.core.scoring.models import History
    from wouso.games.challenge.models import ChallengeUser, ChallengeGame
    from wouso.games.qotd.models import QotdGame
    from wouso.games.quest.models import QuestGame
    from wouso.games.specialquest.models import SpecialQuestGame

    data = []
    header = ['id',
              'player',
              'points',
              'gold',
              'challs',
              'chall_won',
              'chall_lost',
              'chall_points',
              'qotd_points',
              'quest_points',
              'special_gold',
    ]
    data.append(header)
    for p in Player.objects.all():
        chall = p.get_extension(ChallengeUser)
        row = [p.id,
               p,
               p.points,
               p.coins.get('gold', 0),
               chall.get_all_challenges().count(),
               chall.get_won_challenges().count(),
               chall.get_lost_challenges().count(),
               History.user_points_from_game(p.user, ChallengeGame)['points'],
               History.user_points_from_game(p.user, QotdGame)['points'],
               History.user_points_from_game(p.user, QuestGame)['points'],
               History.user_points_from_game(p.user, SpecialQuestGame)['gold'],
        ]
        data.append(row)
    return data

def main(args):
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--peruser', action='store_true')
    parser.add_argument('--activity', action='store_true')
    arguments = parser.parse_args()

    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    if arguments.peruser:
        data = peruser_stats()
        print "Saved to", save_csv('peruser.csv', data)
    elif arguments.activity:
        data = scoring_activity_stats()
        print "Saved to", save_csv('activity.csv', data)
    else:
        main(sys.argv)
