# Create your views here.
from wouso.core.user.models import Player
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from wouso.core.user.models import PlayerGroup
from wouso.interface.top.models import History, TopUser, Top

PERPAGE = 20
def gettop(request, toptype=0, sortcrit=0, page=1):
    # toptype = 0 means overall top
    # toptype = 1 means top for 1 week
    # sortcrit = 0 means sort by points descending
    # sortcrit = 1 means sort by progress descending
    # sortcrit = 2 means sort by last_seen descending
    try:
        toptypeno = int(toptype)
    except:
        toptypeno = 0
    try:
        sortcritno = int(sortcrit)
    except:
        sortcritno = 0
    try:
        pageno = int(page)
    except:
        pageno = 1
    if pageno < 0:
        raise Http404

    base_query = TopUser.objects.exclude(user__is_superuser=True).exclude(groups__name='Others')
    allUsers = base_query.order_by('-points') #[(pageno-1)*PERPAGE:pageno*PERPAGE]
    #if (allUsers.count() == 0):
    #    raise Http404
    #if sortcritno == 1:
    #    allUsers = sorted(TopUser.objects.all(), key = lambda p: p.progress, reverse=True)[(pageno-1)*PERPAGE:pageno*PERPAGE]
    if sortcritno == 2:
        allUsers = base_query.order_by('-last_seen') #[(pageno-1)*PERPAGE:pageno*PERPAGE]

    paginator = Paginator(allUsers, PERPAGE)
    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(0)

    topseries = [] #PlayerGroup.objects.exclude(parent=None).order_by('-points') TODO: top races
    topgroups = PlayerGroup.objects.exclude(parent=None).order_by('-points')[:5]

    return render_to_response('top/maintop.html',
                           {'allUsers':      users,
                            'toptype':       toptypeno,
                            'sortcrit':      sortcritno,
                            'topgroups':      topgroups,
                            'topseries':      topseries,
                            'is_top': True,
                            'top': Top},
                           context_instance=RequestContext(request))

def pyramid(request):
    s = []
    for g in PlayerGroup.objects.exclude(show_in_top=False).filter(parent=None).order_by('name'): #TODO races
        columns = []
        players = []
        i, j = 1, 0
        for p in g.player_set.all().order_by('-points'):
            players.append(p)
            if len(players) == i:
                columns.append(list(players))
                players = []
                i += 1
        g.columns = columns
        s.append(g)

    return render_to_response('top/pyramid.html',
                            {'series': s, 'top': Top},
                            context_instance=RequestContext(request))

def topclasses(request):
    # top classes
    classes = PlayerGroup.objects.exclude(parent=None).order_by('points')
    classes = list(classes)
    classes = reversed(sorted(classes, key=lambda obj: obj.live_points))

    return render_to_response('top/classes.html', {'classes':classes, 'top':Top},
                              context_instance=RequestContext(request))