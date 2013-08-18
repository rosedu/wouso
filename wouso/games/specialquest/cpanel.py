# views for wouso cpanel
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_noop
from django.views.generic import ListView
from wouso.core.user.models import Player
from wouso.core import scoring, signals
from models import SpecialQuestTask, SpecialQuestUser, SpecialQuestGame, SpecialQuestGroup
from forms import TaskForm

class HomeView(ListView):
    model = SpecialQuestTask
    template_name = 'specialquest/cpanel_home.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({'module': 'specialquest'})
        return context

home = permission_required('specialquest.change_specialquestuser')(HomeView.as_view())

class GroupsView(ListView):
    model = SpecialQuestGroup
    template_name = 'specialquest/cpanel_groups.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data(**kwargs)
        context.update({'module': 'specialquest'})
        return context

groups = permission_required('specialquest.change_specialquestuser')(GroupsView.as_view())

@permission_required('specialquest.change_specialquestuser')
def edit(request, id=None):
    if id is not None:
        task = get_object_or_404(SpecialQuestTask, pk=id)
    else:
        task = None

    form = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))

    return render_to_response('specialquest/cpanel_edit.html',
                              {'task': task,
                               'form': form,
                               'module': 'specialquest'},
                              context_instance=RequestContext(request))

@permission_required('specialquest.change_specialquestuser')
def delete(request, id=None):
    if id is None:
        return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))
    task = get_object_or_404(SpecialQuestTask, pk=id)
    task.delete()
    return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))

@permission_required('specialquest.change_specialquestuser')
def manage_player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    player = player.get_extension(SpecialQuestUser)
    tasks_not_done = SpecialQuestTask.objects.exclude(id__in=player.done_tasks.all().values('id')).all()

    # TODO: use smth like django-flash for this
    message, error = '', ''

    if request.method == "POST":
        # do bonuses
        if request.POST.get('gold', False):
            try:
                amount = int(request.POST.get('gold', 0))
            except ValueError:
                amount = 0
            if amount > 0:
                scoring.score(player, None, 'bonus-gold', external_id=request.user.get_profile().id, gold=amount)
                message = 'Successfully given bonus'
                if request.POST.get('comment', None):
                    signal_msg = ugettext_noop('received {gold} gold bonus for {comment}')
                    signals.addActivity.send(sender=None, user_from=player, user_to=player, message=signal_msg,
                                        arguments=dict(gold=amount, comment=request.POST['comment']),
                                        game=SpecialQuestGame.get_instance()
                    )
            else:
                error = 'Invalid amount'
        elif request.POST.get('points', False):
            try:
                amount = int(request.POST.get('points', 0))
                #assert amount > 0
            except (ValueError, AssertionError):
                error = 'Invalid amount'
            else:
                scoring.score(player, None, 'penalty-points', external_id=request.user.get_profile().id, points=amount)
                message = 'Successfully punished'

    bonuses = scoring.History.objects.filter(user=player, formula__name='bonus-gold').order_by('-timestamp')
    penalties = scoring.History.objects.filter(user=player, formula__name='penalty-points').order_by('-timestamp')

    return render_to_response('specialquest/cpanel_manage.html',
                    dict(mplayer=player, tasks_not_done=tasks_not_done, message=message, error=error,
                         bonuses=bonuses, penalties=penalties),
                    context_instance=RequestContext(request))

@permission_required('specialquest.change_specialquestuser')
def manage_player_set(request, player_id, task_id):
    player = get_object_or_404(SpecialQuestUser, id=player_id)
    task = get_object_or_404(SpecialQuestTask, id=task_id)

    if task not in player.done_tasks.all():
        if player.group:
            members = player.group.members
            player.group.set_task_done(task)
        else:
            members = (player,)

        for member in members:
            if task not in member.done_tasks.all():
                member.done_tasks.add(task)
                scoring.score(member, SpecialQuestGame, 'specialquest-passed',external_id=task.id, value=task.value)

                signal_msg = ugettext_noop('completed special quest {task_name} and earned {value} gold')
                action_msg = 'specialq-ok-gold'
                signals.addActivity.send(sender=None, user_from=member, \
                                         user_to=member, \
                                         message=signal_msg,
                                         arguments=dict(task_name=task.name, value=task.value), \
                                         game=SpecialQuestGame.get_instance(),
                                         action=action_msg)

    return HttpResponseRedirect(reverse('specialquest_manage', args=(player.id,)))

@permission_required('specialquest.change_specialquestuser')
def manage_player_unset(request, player_id, task_id):
    player = get_object_or_404(SpecialQuestUser, id=player_id)
    task = get_object_or_404(SpecialQuestTask, id=task_id)

    if task in player.done_tasks.all():
        player.done_tasks.remove(task)
        scoring.unset(player, SpecialQuestGame, 'specialquest-passed', external_id=task.id)
        signal_msg = ugettext_noop('completed special quest {task_name}')
        arguments = dict(task_name=task.name)
        from wouso.interface.activity.models import Activity
        Activity.delete(SpecialQuestGame.get_instance(), player, player, signal_msg, arguments)

    return HttpResponseRedirect(reverse('specialquest_manage', args=(player.id,)))


@permission_required('specialquest.change_specialquestuser')
def group_active_toggle(request, group):
    group = get_object_or_404(SpecialQuestGroup, id=group)

    group.active = not group.active
    group.save()

    return redirect('specialquest_cpanel_groups')


@permission_required('specialquest.change_specialquestuser')
def group_delete(request, group):
    group = get_object_or_404(SpecialQuestGroup, id=group)
    group.destroy()
    return redirect('specialquest_cpanel_groups')


@permission_required('specialquest.change_specialquestuser')
def group_drop_player(request, group, player):
    group = get_object_or_404(SpecialQuestGroup, id=group)
    player = get_object_or_404(SpecialQuestUser, id=player)

    if group.head == player or player not in group.members:
        return redirect('specialquest_group', group_id=group.id)

    group.players.remove(player.user.player_related.get())
    player.group = None
    player.save()

    return redirect('specialquest_group', group_id=group.id)
