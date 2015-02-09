from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from datetime import date
from wouso.core.ui import register_sidebar_block, register_header_link
from wouso.core.user.models import Player
from models import SpecialQuestUser, SpecialQuestTask, SpecialQuestGame, \
    SpecialQuestGroup, Invitation


@login_required
def index(request, error=''):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    tasks_done, tasks_not_done = SpecialQuestGame.tasks_for_user(user)
    today = date.today()
    tasks_not_done = [(t, (t.end_date - today).days + 1)
                      for t in tasks_not_done]

    return render_to_response('specialquest/index.html',
                              {'tasks_done': tasks_done,
                               'tasks_not_done': tasks_not_done,
                               'squser': user, 'error': error},
                              context_instance=RequestContext(request))


@login_required
def task(request, task_id):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    t = get_object_or_404(SpecialQuestTask, pk=task_id)
    done = (t in user.done_tasks.all())
    days_left = (t.end_date - date.today()).days
    days_left += 1  # including current day

    return render_to_response('specialquest/task.html',
                              {'task': t, 'done': done,
                               'days_left': days_left},
                              context_instance=RequestContext(request))


@login_required
def setup_accept(request, group_id):
    MAX_GROUP_MEMBERS = 4
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    group = get_object_or_404(SpecialQuestGroup, pk=group_id)

    if group.active:
        error = _('Group is already active, you cannot accept the invitation')
        messages.error(request, error)
        return HttpResponseRedirect(reverse('specialquest_index_view'))

    if user.group is not None:
        error = _('You are already in a group, cannot accept the invitation')
        messages.error(request, error)
        return HttpResponseRedirect(reverse('specialquest_index_view'))

    if group.players.count() >= MAX_GROUP_MEMBERS:
        error = _('Group is full, you cannot accept the invitation')
        messages.error(request, error)
        return HttpResponseRedirect(reverse('specialquest_index_view'))

    user.add_to_group(group)

    return HttpResponseRedirect(reverse('specialquest_index_view'))


@login_required
def setup_leave(request):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    group = user.group
    group.remove(user)
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
    error = ''
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

    if error:
        messages.error(request, error)

    return render_to_response('specialquest/create.html',
                              context_instance=RequestContext(request))


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

    if error:
        messages.error(request, error)
    if message:
        messages.success(request, message)

    return render_to_response('specialquest/invite.html',
                              dict(to_user=to_user, squser=user),
                              context_instance=RequestContext(request))


@login_required
def view_group(request, group_id):
    group = get_object_or_404(SpecialQuestGroup, pk=group_id)

    return render_to_response('specialquest/group.html',
                              dict(sqgroup=group),
                              context_instance=RequestContext(request))


def sidebar_widget(context):
    user = context.get('user', None)
    if SpecialQuestGame.disabled() or not user or not user.is_authenticated():
        return ''
    user = user.get_profile().get_extension(SpecialQuestUser)
    count = len(user.active_tasks)

    if not count:
        return ''

    return render_to_string('specialquest/sidebar.html',
                            {'not_done': count})


register_sidebar_block('specialquest', sidebar_widget)


def header_link(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated() or SpecialQuestGame.disabled():
        return {}
    profile = user.get_profile()
    if profile:
        user = profile.get_extension(SpecialQuestUser)
        count = len(user.active_tasks)
    else:
        count = 0
    url = reverse('wouso.games.specialquest.views.index')

    return dict(link=url, count=count, text=_('Special'))


register_header_link('specialquest', header_link)
