# coding=utf-8
from datetime import datetime, timedelta, date
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
import json
from wouso.core.decorators import staff_required
from wouso.games.challenge.models import Challenge
from wouso.games.qotd.models import QotdUser
from wouso.core.user.models import Player
from wouso.games.quest.models import Quest, QuestGame
from wouso.interface.activity.models import Activity


def stats(request):

    data = {}

    # now
    try:
        users_online_now = Player.objects.filter(
            last_seen__gte=datetime.now() - timedelta(minutes=10))
    except:
        users_online_now = []
    data['users_online_now'] = len(users_online_now)

    # today
    today = date.today()
    try:
        users_online_today = Player.objects.filter(last_seen__gte=today)
    except:
        users_online_today = []
    data['users_online_today'] = len(users_online_today)

    try:
        challenges_played_today = Challenge.objects.filter(date__year=today.year,
                                                           date__month=today.month,
                                                           date__day=today.day).filter(
            Q(status='P') | Q(status='D'))
    except:
        challenges_played_today = []
    data['challenges_played_today'] = len(challenges_played_today)

    try:
        qotd_answers_today = QotdUser.objects.filter(last_answered__gte=today)
    except:
        qotd_answers_today = []
    data['qotd_answers_today'] = len(qotd_answers_today)

    # week
    week_start = date.today() - timedelta(days=date.today().isocalendar()[2])
    try:
        users_online_week = Player.objects.filter(last_seen__gte=week_start)
    except:
        users_online_week = []
    data['users_online_week'] = len(users_online_week)

    try:
        challenges_played_week = Challenge.objects.filter(date__gte=week_start).filter(
            Q(status='P') | Q(status='D'))
    except:
        challenges_played_week = []
    data['challenges_played_week'] = len(challenges_played_week)

    try:
        qotd_answers_week = QotdUser.objects.filter(last_answered__gte=week_start)
    except:
        qotd_answers_week = []
    data['qotd_answers_week'] = len(qotd_answers_week)

    # ever
    try:
        users_online_ever = Player.objects.filter(last_seen__isnull=False)
    except:
        users_online_ever = []
    data['users_online_ever'] = len(users_online_ever)

    try:
        challenges_played_ever = Challenge.objects.filter(
            Q(status='P') | Q(status='D'))
    except:
        challenges_played_ever = []
    data['challenges_played_ever'] = len(challenges_played_ever)

    try:
        qotd_answers_ever = QotdUser.objects.filter(last_answered__isnull=False)
    except:
        qotd_answers_ever = []
    data['qotd_answers_ever'] = len(qotd_answers_ever)

    return render_to_response('statistics/stats.html', data,
                              context_instance=RequestContext(request))


def footer_link(request):
    link = '<a id="page-special-statistics" href="'+ reverse('wouso.interface.apps.statistics.views.stats') +'">' + _('Live stats') + '</a>'
    return link


@staff_required
def extra_stats(request):
    """
    Generate extra statistics, dump them as JSON

    * Numărul de jucători care au accesat în 95% din zile site-ul
    * Numărul total de provocări rulate
    * Numărul maxim de provocări jucate într-o zi
    * Media numărul de provocări jucate într-o zi
    * Numărul de jucători care au răspuns la cel puțin 75% din QoTD-uri
    * Numărul mediu de răspunsuri pe zi la QotD
    * Media numărului de jucători care au ajuns cel puțin la nivelul 5 din
      weekly quest (vezi câți au ajuns la nivelul 5 din weekly quest în
      fiecare weekly quest și apoi faci media lor).
    * Media numărului de jucători care au ajuns la nivelul 10 din
      weekly quest
    * Pentru final quest (când se va încheia): câți jucători l-au început,
      câți l-au terminat, câți au ajuns cel puțin la nivelul 25, 20, 15.
    """
    data = {}

    # Seen
    seen_basequery = Activity.objects.filter(action='seen')
    seen_days_count = seen_basequery.dates('timestamp', 'day').count()
    s95 = int(0.95 * seen_days_count)
    su95 = 0
    for u in seen_basequery.values('user_from').distinct():
        if seen_basequery.filter(user_from=u['user_from']).dates('timestamp', 'day').count() >= s95:
            su95 += 1
    data['seen_all_days'] = seen_days_count
    data['seen_more_than_95'] = su95

    # Challenge
    chall_basequery = Challenge.objects.filter(status__in=('P', 'D'))
    chall_counts = []
    for d in chall_basequery.dates('date', 'day'):
        chall_counts.append(chall_basequery.filter(date__range=(d, d + timedelta(days=1))).count())
    data['challenge_all'] = chall_basequery.count()
    data['challenge_all_days'] = chall_basequery.dates('date', 'day').count()
    data['challenge_min_perday'] = min(chall_counts)
    data['challenge_max_perday'] = max(chall_counts)

    # Qotd
    qotd_basequery = Activity.objects.filter(action__in=('qotd-correct', 'qotd-wrong'))
    qotd_days = qotd_basequery.dates('timestamp', 'day').count()
    q75 = int(0.75 * qotd_days)
    qu75 = 0
    for u in qotd_basequery.values('user_from').distinct():
        cnt = qotd_basequery.filter(user_from=u['user_from']).count()
        if cnt > q75:
            qu75 += 1
    data['qotd_all'] = qotd_basequery.count()
    data['qotd_all_days'] = qotd_days
    data['qotd_perday_average'] = int(1.0 * data['qotd_all'] / data['qotd_all_days'])
    data['qotd_answered_more_75'] = qu75

    # Quest
    ql5 = 0
    ql10 = 0
    for quest in Quest.objects.all():
        if quest.is_final():
            continue
        ql5 += quest.questresult_set.filter(level__gte=5).count()
        ql10 += quest.questresult_set.filter(level__gte=10).count()
    qall = Quest.objects.all().count()
    if QuestGame.final_exists():
        qall -= 1

    if qall:
        ql5 = int(1.0 * ql5 / qall)
        ql10 = int(1.0 * ql10 / qall)
    data['quest_reached_5'] = ql5
    data['quest_reached_10'] = ql10

    # Pack and print
    return HttpResponse(json.dumps(data))