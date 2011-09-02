from hashlib import md5
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.user.models import UserProfile
from wouso.core.scoring.models import History
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser

@login_required
def profile(request):
    list = Activity.objects.all().order_by('-timestamp')[:10]
    return render_to_response('profile/index.html',
                              {'activity': list},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request, id, page=u'0'):
    try:
        profile = UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        raise Http404

    avatar = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid"\
        % md5(profile.user.email).hexdigest()
    activity_list = Activity.objects.\
        filter(Q(user_to=id) | Q(user_from=id)).order_by('-timestamp')

    top_user = profile.get_extension(TopUser)
    history = History.user_points(profile)
    paginator = Paginator(activity_list, 10)

    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

    return render_to_response('profile/profile.html',
                              {'profile': profile,
                               'avatar': avatar,
                               'activity': activity,
                               'top': top_user,
                               'scoring': history},
                              context_instance=RequestContext(request))
