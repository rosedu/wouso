from datetime import datetime, timedelta
from hashlib import md5
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.scoring.models import History
from wouso.core.magic.models import Spell, PlayerSpellDue
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser, GroupHistory
from wouso.interface.top.models import History as TopHistory
from wouso.core.game import get_games

@login_required
def profile(request):
    # TODO: remove this and url to this
    list = Activity.objects.all().order_by('-timestamp')[:10]
    return render_to_response('profile/index.html',
                              {'activity': list},
                              context_instance=RequestContext(request))

@login_required
def player_points_history(request, id):
    player = get_object_or_404(Player, pk=id)
    hist = History.objects.filter(user=player).order_by('-timestamp')[:500]
    return render_to_response('profile/points_history.html',
                            {'pplayer': player, 'history': hist},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request, id, page=u'1'):
    try:
        profile = Player.objects.get(id=id)
    except Player.DoesNotExist:
        raise Http404

    avatar = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid"\
        % md5(profile.user.email).hexdigest()
    activity_list = Activity.objects.\
        filter(Q(user_to=id) | Q(user_from=id)).order_by('-timestamp')

    top_user = profile.get_extension(TopUser)
    top_user.topgroups = list(profile.groups.all())
    for g in top_user.topgroups:
        g.week_evolution = top_user.week_evolution(relative_to=g)
        g.position = TopHistory.get_user_position(top_user, relative_to=g)
    history = History.user_points(profile)
    paginator = Paginator(activity_list, 10)

    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

    profile_actions = ''
    profile_superuser_actions = ''
    for g in get_games():
        profile_actions += g.get_profile_actions(request, profile)
        profile_superuser_actions += g.get_profile_superuser_actions(request, profile)

        # some hackish introspection
        if hasattr(g, 'user_model'):
            model = getattr(g, 'user_model')
            setattr(profile, model.__name__.lower(), profile.get_extension(model))

    return render_to_response('profile/profile.html',
                              {'profile': profile,
                               'avatar': avatar,
                               'activity': activity,
                               'top': top_user,
                               'scoring': history,
                               'profile_actions': profile_actions,
                               'profile_superuser_actions': profile_superuser_actions,},
                              context_instance=RequestContext(request))

@login_required
def player_group(request, id, page=u'1'):
    group = get_object_or_404(PlayerGroup, pk=id)

    top_users = group.player_set.all().order_by('-points')
    subgroups = group.children.order_by('-points')
    if group.parent:
        sistergroups = group.parent.children.all().order_by('-points')
    else:
        sistergroups = None
    history = GroupHistory(group)

    for g in group.sisters:
        g.top = GroupHistory(g)

    activity_list = Activity.objects.\
        filter(Q(user_to__groups=group) | Q(user_from__groups=group)).distinct().order_by('-timestamp')
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

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
    PlayerGroup.top = lambda(self): GroupHistory(self)
    groups = PlayerGroup.objects.exclude(parent=None).order_by('name')
    
    return render_to_response('profile/groups.html',
                              {'groups': groups},
                              context_instance=RequestContext(request))

@login_required
def magic_cast(request, destination=None, spell=None):
    player = request.user.get_profile()
    destination = get_object_or_404(Player, pk=destination)

    error = ''

    if request.method == 'POST':
        spell = get_object_or_404(Spell, pk=request.POST.get('spell', 0))
        try:
            days = int(request.POST.get('days', 0))
        except ValueError:
            pass
        else:
            if (days > spell.due_days) or ((spell.due_days > 0) and (days < 1)):
                error = _('Invalid number of days')
            else:
                due = datetime.now() + timedelta(days=days)
                if destination.magic.cast_spell(spell, source=player, due=due):
                    return HttpResponseRedirect(reverse('wouso.interface.profile.views.user_profile', args=(destination.id,)))
                else:
                    error = _('Cast failed.')

    return render_to_response('profile/cast.html',
                              {'destination': destination, 'error': error},
                              context_instance=RequestContext(request))

@login_required
def magic_summary(request):
    """ Display a summary of spells cast by me or on me """
    player = request.user.get_profile()

    cast_spells = PlayerSpellDue.objects.filter(source=player).all()

    return render_to_response('profile/spells.html',
                              {'cast': cast_spells,
                              'theowner': player},
                              context_instance=RequestContext(request))

@login_required
def magic_spell(request):
    try:
        spell = int(request.GET.get('id', None))
    except:
        raise Http404
    spell = get_object_or_404(Spell, pk=spell)
    
    return HttpResponse(serializers.serialize('json', (spell,)))
