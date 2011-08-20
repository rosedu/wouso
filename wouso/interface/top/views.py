# Create your views here.
from wouso.interface import render_response
from wouso.core.user.models import UserProfile
from django.http import Http404
from wouso.interface.top.models import History, TopUser

PERPAGE = 5;
def gettop(request, sortcrit, page):
    next_page = 0;
    prev_page = 0;
    try:
        pageno = int(page);
    except:
        pageno = 1;
    try:
        sortcritno = int(sortcrit);
    except:
        sortcritno = 0;
    if (pageno < 0):
        raise Http404;

#    allUsers = TopUser.objects.all()[(page - 1)*PERPAGE:page*PERPAGE];
    allUsers = TopUser.objects.order_by('-points')[(pageno-1)*PERPAGE:pageno*PERPAGE];
    if sortcritno == 1:
        allUsers = TopUser.objects.order_by('user__first_name')[(pageno-1)*PERPAGE:pageno*PERPAGE];
    if (allUsers.count() == 0):
        raise Http404;

    count = UserProfile.objects.count();
    if (count > pageno*PERPAGE+PERPAGE):
        next_page = pageno + 1;
    if pageno > 1:
        prev_page = pageno - 1;
    return render_response('top/maintop.html', request, {'allUsers':      allUsers,
                                                         'sortcrit':      sortcritno,
                                                         'page_top_next': next_page,
                                                         'page_top_prev': prev_page});

