from datetime import datetime, timedelta, time, date
from django.http import HttpResponse
from django.db.models import Q
from wouso.core.qpool.models import Question
from wouso.games.challenge.models import Challenge
from wouso.games.qotd.models import QotdUser
from wouso.core.user.models import UserProfile


def stats(request):

    data = {}

    # now
    try:
        users_online_now = UserProfile.objects.filter(
            last_seen__gte=datetime.now() - timedelta(minutes=10))
    except:
        users_online_now = []
    data['users_online_now'] = len(users_online_now)

    # today
    today = date.today()
    try:
        users_online_today = UserProfile.objects.filter(last_seen__gte=today)
    except:
        users_online_today = []
    data['users_online_today'] = len(users_online_today)

    try:
        challenges_played_today = Challenge.objects.filter(date=today).get(
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
        users_online_week = UserProfile.objects.filter(last_seen__gte=week_start)
    except:
        users_online_week = []
    data['users_online_week'] = len(users_online_week)

    try:
        challenges_played_week = Challenge.objects.filter(date=week_start).get(
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
        users_online_ever = UserProfile.objects.filter(last_seen__isnull=False)
    except:
        users_online_ever = []
    data['users_online_ever'] = len(users_online_ever)

    try:
        challenges_played_ever = Challenge.objects.get(
            Q(status='P') | Q(status='D'))
    except:
        challenges_played_ever = []
    data['challenges_played_ever'] = len(challenges_played_ever)

    try:
        qotd_answers_ever = QotdUser.objects.filter(last_answered__isnull=False)
    except:
        qotd_answers_ever = []
    data['qotd_answers_ever'] = len(qotd_answers_ever)

    return HttpResponse(repr(data))
