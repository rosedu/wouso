from datetime import datetime, timedelta, time, date
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.qpool.models import Question
from wouso.games.challenge.models import Challenge
from wouso.games.qotd.models import QotdUser
from wouso.core.user.models import Player


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
    link = '<a id="page-special-statistics" href="'+ reverse('wouso.interface.statistics.views.stats') +'">' + _('Live stats') + '</a>'
    return link
