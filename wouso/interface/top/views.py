# Create your views here.
from wouso.interface import render_response
from wouso.core.user.models import UserProfile
from django.http import Http404
from wouso.interface.top.models import History, TopUser

PERPAGE = 5;
def gettop(request, toptype, sortcrit, page):
    # toptype = 0 means overall top
    # toptype = 1 means top for 1 week
    # sortcrit = 0 means sort by points descending
    # sortcrit = 1 means sort by progress descending
    # sortcrit = 2 means sort by last_seen descending
    next_page = 0;
    prev_page = 0;
    try:
        toptypeno = int(toptype);
    except:
        toptypeno = 0;
    try:
        sortcritno = int(sortcrit);
    except:
        sortcritno = 0;
    try:
        pageno = int(page);
    except:
        pageno = 1;
    if pageno < 0:
        raise Http404;

    allUsers = TopUser.objects.order_by('-points')[(pageno-1)*PERPAGE:pageno*PERPAGE];
    if (allUsers.count() == 0):
        raise Http404;
    if sortcritno == 1:
        allUsers = sorted(TopUser.objects.all(), key = lambda p: p.progress, reverse=True)[(pageno-1)*PERPAGE:pageno*PERPAGE];
    if sortcritno == 2:
        allUsers = TopUser.objects.order_by('-last_seen')[(pageno-1)*PERPAGE:pageno*PERPAGE];

    count = UserProfile.objects.count();
    if (count > pageno*PERPAGE+PERPAGE):
        next_page = pageno + 1;
    if pageno > 1:
        prev_page = pageno - 1;
    return render_response('top/maintop.html', request, {'allUsers':      allUsers,
                                                         'toptype':       toptypeno,
                                                         'sortcrit':      sortcritno,
                                                         'page_top_next': next_page,
                                                         'page_top_prev': prev_page});

