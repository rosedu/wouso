from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.db.models import Q
from wouso.interface import render_response
from wouso.core.user.models import UserProfile
from wouso.interface.activity.models import Activity

@login_required
def profile(request):
    list = Activity.objects.all().order_by('-timestamp')[:10]
    return render_response('profile/index.html', request, \
            {'activity': list})

@login_required
def user_profile(request, id, page=u'0'):
    try:
        profile = UserProfile.objects.get(id=id)
        activity_list = Activity.objects.\
            filter(Q(user_to=id) | Q(user_from=id)).order_by('-timestamp')
        paginator = Paginator(activity_list, 10)
    except UserProfile.DoesNotExist:
        raise Http404

    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

    return render_response('profile/profile.html',
        request,
        {'profile': profile, 'activity': activity})
