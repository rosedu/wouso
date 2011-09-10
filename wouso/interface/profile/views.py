from hashlib import md5
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.scoring.models import History
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser, GroupHistory

@login_required
def profile(request):
    list = Activity.objects.all().order_by('-timestamp')[:10]
    return render_to_response('profile/index.html',
                              {'activity': list},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request, id, page=u'0'):
    try:
        profile = Player.objects.get(id=id)
    except Player.DoesNotExist:
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

@login_required
def player_group(request, id):
    group = get_object_or_404(PlayerGroup, pk=id)

    top_users = group.player_set.all().order_by('-points')
    subgroups = group.children.order_by('-points')
    if group.parent:
        sistergroups = group.parent.children.order_by('-points')
    else:
        sistergroups = PlayerGroup.objects.filter(gclass=group.gclass).order_by('-points')
    history = GroupHistory(group)

    for g in group.sisters:
        g.top = GroupHistory(g)

    activity_list = Activity.objects.\
        filter(Q(user_to__groups=group) | Q(user_from__groups=group)).order_by('-timestamp')
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(1)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(1)

    return render_to_response('profile/group.html',
                              {'group': group,
                               'top_users': top_users,
                               'subgroups': subgroups,
                               'sistergroups': sistergroups,
                               'top': history,
                               'activity': activity,
                               },
                              context_instance=RequestContext(request))

@login_required
def groups_index(request):
    groups = PlayerGroup.objects.filter(gclass=1).order_by('name')

    return render_to_response('profile/groups.html',
                              {'groups': groups},
                              context_instance=RequestContext(request))
