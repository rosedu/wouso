# Create your views here.
from wouso.interface import render_response
from wouso.core.user.models import UserProfile
from django.http import Http404
from wouso.interface.top.models import History, TopUser

PERPAGE = 5;
def gettop(request):
    next_page = 0;
    prev_page = 0;
    try:
        page = int(request.GET.get('p', 1));
    except:
        raise Http404;
    if (page < 1):
        raise Http404;

    allUsers = TopUser.objects.all()[(page - 1)*PERPAGE:page*PERPAGE];
    if (allUsers.count() == 0):
        raise Http404;

    count = UserProfile.objects.count();
    if (count > page*PERPAGE+PERPAGE):
        next_page = page + 1;
    if page:
        prev_page = page - 1;
    return render_response('top/maintop.html', request,
                            {'allUsers': allUsers,
                            'page_top_next' : next_page,
                            'page_top_prev' : prev_page});
