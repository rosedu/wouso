from django.contrib.auth.decorators import login_required
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
def user_profile(request, id):
    try:
        profile = UserProfile.objects.get(id=id)
        activity = Activity.objects.filter(Q(user_to=id) | Q(user_from=id)).order_by('-timestamp')[:10]
    except UserProfile.DoesNotExist:
        raise Http404

    return render_response('profile/profile.html',
        request,
        {'profile': profile, 'activity': activity})
