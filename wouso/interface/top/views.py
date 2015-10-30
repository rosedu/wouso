# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from wouso.core.scoring import Coin
from wouso.core.user.models import Race
from wouso.core.user.models import PlayerGroup
from wouso.interface.top.models import TopUser, Top, NewHistory

PERPAGE = 20
TOPGROUPS_NO = 5

def pyramid(request):
    s = []
    for r in Race.objects.exclude(can_play=False).order_by('name'):
        columns = []
        players = []
        i, j = 1, 0
        for p in r.player_set.all().order_by('-points'):
            players.append(p)
            if len(players) == i:
                columns.append(list(players))
                players = []
                i += 1
        r.columns = columns
        s.append(r)

    return render_to_response('top/pyramid.html',
                            {'series': s, 'top': Top},
                            context_instance=RequestContext(request))

def topclasses(request):
    # top classes

    # get reversed sorted list of classes belonging to a race which can play
    classes = PlayerGroup.objects.exclude(parent=None).exclude(parent__can_play=False).order_by('points')
    classes = list(classes)
    classes.sort(key=lambda obj: obj.live_points, reverse=True)

    # get reversed sorted list of classes belonging to a race which cannot play
    cannotplay_classes = PlayerGroup.objects.exclude(parent=None).exclude(parent__can_play=True).order_by('points')
    cannotplay_classes = list(cannotplay_classes)
    cannotplay_classes.sort(key=lambda obj: obj.live_points, reverse=True)

    # append cannotplay_classes to classes
    classes.extend(cannotplay_classes)

    return render_to_response('top/classes.html', {'classes':classes, 'top':Top},
                              context_instance=RequestContext(request))

def topraces(request):
    # top races
    races = list(Race.objects.exclude(can_play=False))
    races.sort(key=lambda a: a.points, reverse=True)
    return render_to_response('top/races.html', {'races':races, 'top':Top},
                                context_instance=RequestContext(request))

def challenge_top(request, sortcritno='0', pageno=1):
    #sortcrit = 0 descending order of wins
    #sortcrit = 1 descending order of % wins
    #sortcrit = 2 descending order of losses
    base_query = TopUser.objects.exclude(user__is_superuser=True).exclude(race__can_play=False)

    if sortcritno == '0':
        allUsers = sorted(base_query, key=lambda x: -x.won_challenges)
    elif sortcritno == '1':
        allUsers = sorted(base_query, key=lambda x: -x.won_perc_challenges)
    else :
        allUsers = sorted(base_query, key=lambda x: -x.lost_challenges)

    paginator = Paginator(allUsers, PERPAGE)
    try:
        users = paginator.page(int(pageno))
    except (EmptyPage, InvalidPage):
        users = paginator.page(1)

    # get reversed sorted list of series
    topseries = list(Race.objects.exclude(can_play=False))
    topseries.sort(key=lambda a: a.points, reverse=True)

    # get first TOPGROUPS_NO items from reversed sorted list of groups belonging to a 'can play' race
    topgroups = PlayerGroup.objects.exclude(parent=None).exclude(parent__can_play=False).order_by('points')
    topgroups = list(topgroups)
    topgroups.sort(key=lambda obj: obj.live_points, reverse=True)
    topgroups = topgroups[:TOPGROUPS_NO]

    return render_to_response('top/challenge_top.html', {
                    'allUsers': users,
                    'sortcritno': sortcritno,
                    'topgroups': topgroups,
                    'topseries': topseries,
                    'is_top': True,
                    'top': Top
                    }, context_instance=RequestContext(request))

def topcoin(request, coin):
    coin_obj = Coin.get(coin)
    if coin_obj is None:
        raise Http404

    pageno = request.GET.get('page', 0)
    topcoin_qs = NewHistory.get_coin_top(coin_obj)
    paginator = Paginator(topcoin_qs, PERPAGE)
    try:
        pageno = int(pageno)
        topcoin = paginator.page(pageno)
    except (EmptyPage, InvalidPage, ValueError):
        pageno = 1
        topcoin = paginator.page(pageno)


    return render_to_response('top/coin_top.html',
                {'top': topcoin, 'coin': coin_obj, 'page_start': (pageno - 1)* PERPAGE},
                context_instance=RequestContext(request)
    )