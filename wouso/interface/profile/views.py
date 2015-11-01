from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.html import strip_tags

from wouso.core.config.models import BoolSetting
from wouso.core.god import God
from wouso.core.magic.models import Spell, PlayerSpellDue
from wouso.core.scoring.models import History
from wouso.core.user.models import Player, PlayerGroup, Race
from wouso.games.challenge.models import Challenge
from wouso.games.specialquest.models import SpecialQuestGame
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser, GroupHistory, NewHistory, ObjectHistory


@login_required
def player_points_history(request, id):
    player = get_object_or_404(Player, pk=id)
    hist = History.objects.filter(user=player).order_by('-timestamp')[:500]
    return render_to_response('profile/points_history.html',
                              {'pplayer': player, 'history': hist},
                              context_instance=RequestContext(request))


@login_required
def set_profile(request):
    user = request.user.get_profile()

    class SForm(forms.ModelForm):
        class Meta:
            model = Player
            fields = ('nickname',)

        def clean_nickname(self):
            if Player.objects.exclude(id=self.instance.id).filter(nickname=self.cleaned_data['nickname']).count():
                raise ValidationError("Nickname is used")
            self.cleaned_data['nickname'] = strip_tags(self.cleaned_data['nickname'].strip().replace(' ', '_'))
            return self.cleaned_data['nickname']


    if request.method == 'POST':
        form = SForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('player_profile', id=user.id)
    else:
        form = SForm(instance=user)

    return render_to_response('profile/set_profile.html',
                              {'profile': user, 'form': form},
                              context_instance=RequestContext(request))


@login_required
def save_profile(request):
    # TODO: clean this mess
    user = request.user.get_profile()
    data = request.REQUEST

    try:
        Player.objects.exclude(nickname = user.nickname).get(nickname = data['nickname'])
        #print "exista!"
        return HttpResponseBadRequest()
    except:
        user.nickname = data['nickname']
        user.user.first_name = data['firstname']
        user.description = data['description']
        user.save()
        user.user.save()
    return HttpResponse()


@login_required
def user_profile(request, id, page=u'1'):
    profile = get_object_or_404(Player, id=id)

    activity_list = Activity.get_player_activity(profile)

    top_user = profile.get_extension(TopUser)
    history = History.user_points(profile.user)
    paginator = Paginator(activity_list, 10)

    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

        # some hackish introspection
        if hasattr(g, 'user_model'):
            model = getattr(g, 'user_model')
            setattr(profile, model.__name__.lower(), profile.get_extension(model))
    #Fix to show succes message from report user form
    if 'report_msg' in request.session:
        message = request.session['report_msg']
        del request.session['report_msg']
    else:
        message=''

    challenge_launched_recently = Challenge.exist_last_day(date.today(),
                                        request.user.get_profile(), profile)
    specialquest_button = SpecialQuestGame.get_specialquest_user_button(request, profile)
    config_disable_magic = BoolSetting.get('disable-Magic').get_value()

    return render_to_response('profile/profile.html',
                              {'profile': profile,
                               'activity': activity,
                               'top': top_user,
                               'scoring': history,
                               'challenge_launched_recently': challenge_launched_recently,
                               'specialquest_button': specialquest_button,
                               'config_disable_magic': config_disable_magic,
                               'message': message},
                              context_instance=RequestContext(request))


@login_required
def player_group(request, id, page=u'1'):
    group = get_object_or_404(PlayerGroup, pk=id)

    top_users = group.players.all().order_by('-points')
    subgroups = group.children
    if group.parent:
        sistergroups = NewHistory.get_children_top(group.parent, PlayerGroup)
    else:
        sistergroups = None
    history = GroupHistory(group)

    for g in group.sisters:
        g.top = GroupHistory(g)

    activity_list = Activity.get_group_activiy(group)
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
def player_race(request, race_id):
    race = get_object_or_404(Race, pk=race_id)

    top_users = race.player_set.order_by('-points')
    activity_qs = Activity.get_race_activity(race)
    paginator = Paginator(activity_qs, 20)
    activity = paginator.page(1)

    # get top position
    races = list(Race.objects.filter(can_play=True))
    races.sort(key=lambda a: a.points, reverse=True)
    if race in races:
        top_rank = races.index(race) + 1
    else:
        top_rank = '-'

    groups = NewHistory.get_children_top(race, PlayerGroup)

    # Get levels
    levels = []
    for i, limit in enumerate(God.get_level_limits()):
        l = God.get_race_level(level_no=i + 1, race=race)
        l.limit = limit
        levels.append(l)

    return render_to_response('profile/race.html',
                            {'race': race,
                             'children': groups,
                             'top_users': top_users,
                             'top_rank': top_rank,
                             'top': ObjectHistory(),
                             'activity': activity,
                             'levels': levels},
                            context_instance=RequestContext(request)
    )


@login_required
def groups_index(request):
    PlayerGroup.top = lambda(self): GroupHistory(self)
    groups = PlayerGroup.objects.exclude(parent=None).order_by('name')

    return render_to_response('profile/groups.html',
                              {'groups': groups},
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
