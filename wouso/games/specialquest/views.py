from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from wouso.interface import render_string
from wouso.core.user.models import Player
from models import SpecialQuestUser, SpecialQuestTask, SpecialQuestGame, SpecialQuestGroup, Invitation


@login_required
def index(request, error=''):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    tasks_done, tasks_not_done = SpecialQuestGame.tasks_for_user(user)
    today = date.today()
    tasks_not_done = [(t, (t.end_date - today).days + 1) for t in tasks_not_done]

    return render_to_response('specialquest/index.html',
                    {'tasks_done': tasks_done, 'tasks_not_done': tasks_not_done,
                     'squser': user, 'error': error},
                    context_instance=RequestContext(request))

def task(request, task_id):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    t = get_object_or_404(SpecialQuestTask, pk=task_id)
    done = (t in user.done_tasks.all())
    days_left = (t.end_date - date.today()).days
    days_left += 1 # including current day

    return render_to_response('specialquest/task.html',
                    {'task': t, 'done': done, 'days_left': days_left},
                    context_instance=RequestContext(request))

@login_required
def setup_accept(request, group_id):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    group = get_object_or_404(SpecialQuestGroup, pk=group_id)

    if group.active:
        error = _('Group is already active, you cannot accept the invitation')
        return index(request, error)

    user.group = group
    user.save()
    group.players.add(request.user.get_profile())

    return HttpResponseRedirect(reverse('specialquest_index_view'))

@login_required
def setup_leave(request):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    group = user.group
    if group is None or group.active or ((group.head == user) and not group.is_empty()):
        # do nothing
        pass
    else:
        user.group = None
        user.save()
        if group.head == user:
            group.delete()

    return HttpResponseRedirect(reverse('specialquest_index_view'))

@login_required
def setup_create(request):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    group = user.group
    error, message = '', ''
    if group is not None:
        error = _('You already have a group')
    else:
        if request.method == "POST":
            name = request.POST.get('name', '')
            if not name:
                error = _('Please specify a name')
            else:
                eg = SpecialQuestGroup.objects.filter(name=name).count()
                if eg:
                    error = _('A group with this name already exists')
                else:
                    group = SpecialQuestGroup.create(head=user, name=name)
                    return HttpResponseRedirect(reverse('specialquest_index_view'))

    return render_to_response('specialquest/create.html', dict(error=error), context_instance=RequestContext(request))

@login_required
def setup_invite(request, user_id):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    to_user = get_object_or_404(Player, pk=user_id)
    to_user = to_user.get_extension(SpecialQuestUser)
    group = user.group
    error, message = '', ''
    if group is None:
        error = _("You don't have a group")
    elif to_user.group is not None:
        error = _("User already in a group")
    else:
        if request.method == "POST":
            Invitation.objects.create(group=user.group, to=to_user)
            message = _("Invitation sent")

    return render_to_response('specialquest/invite.html', dict(error=error, message=message, to_user=to_user, squser=user),
                              context_instance=RequestContext(request))

@login_required
def view_group(request, group_id):
    group = get_object_or_404(SpecialQuestGroup, pk=group_id)

    return render_to_response('specialquest/group.html', dict(sqgroup=group), context_instance=RequestContext(request))

def sidebar_widget(request):
    if SpecialQuestGame.disabled():
        return ''
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    tasks = SpecialQuestTask.objects.all()
    today = date.today()
    tasks = [t for t in tasks if t not in user.done_tasks.all() and t.start_date <= today <= t.end_date]

    if not tasks:
        return ''

    return render_to_string('specialquest/sidebar.html', {'not_done': len(tasks)})

def header_link(request):
    profile = request.user.get_profile()
    if SpecialQuestGame.disabled():
        return None
    if profile:
        user = profile.get_extension(SpecialQuestUser)
        tasks = SpecialQuestTask.objects.all()
        today = date.today()
        tasks = [t for t in tasks if t not in user.done_tasks.all() and t.start_date <= today <= t.end_date]

        count = len(tasks)
    else:
        count = 0
    url = reverse('wouso.games.specialquest.views.index')
    
    return dict(link=url, count=count, text=_('Special'))
