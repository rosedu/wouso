from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View
from wouso.core.ui import register_sidebar_block
from wouso.core.user.models import Player
from wouso.core.qpool.models import Question, Answer, Category
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from models import *
from forms import *


class TeamHubView(DetailView):
    model = TeamQuestUser
    template_name = 'teamquest/teamhub.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(TeamHubView, self).get_context_data(**kwargs)
        quest_user = self.get_object()
        context['group'] = quest_user.group
        context['ownership'] = quest_user.is_group_owner()
        if quest_user.group is None:
            context['invitations'] = TeamQuestInvitation.objects.filter(to_user=quest_user)
            context['create_form'] = CreateGroupForm()
            context['request_form'] = RequestToJoinForm()
        if quest_user.is_group_owner():
            context['requests'] = TeamQuestInvitationRequest.objects.filter(to_group=quest_user.group)
            context['invite_form'] = InvitePlayerForm()
        return context

teamhub = login_required(TeamHubView.as_view())


@login_required
def setup_create(request):
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group:
        messages.error(request, _("Puny human, you already have a team!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))
    form = CreateGroupForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        if TeamQuestGroup.objects.filter(name=name).count():
            messages.error(request, _("Unfortunately you were not the first to think of that name. Choose another!"))            
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))
        TeamQuestGroup.create(group_owner=user, name=name)

        messages.success(request,
            _("You are now the leader of the team %(gn)s. Good luck in your adventures!")
            % {'gn': name})

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_invite(request):
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group is None or not user.is_group_owner():
        messages.error(request, _("Puny human, you can not invite someone to join your team!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    form = InvitePlayerForm(request.POST)
    if form.is_valid():
        invited_user = form.cleaned_data['to_user']

        if TeamQuestInvitation.objects.filter(to_user=invited_user, from_group=group).count():
            messages.error(request,
                _("Puny human, you already invited %(pn)s to join your team. Be patient!")
                % {'pn': invited_user.nickname})
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

        if invited_user.group is not None:
            messages.error(request, _("This player already has a team."))
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

        TeamQuestInvitation.objects.create(to_user=invited_user, from_group=group)
        messages.success(request,
            _("You have invited %(pn)s to join your team!")
            % {'pn': invited_user.nickname})

    else:
        messages.error(request, _("Puny human, you need to select somebody!"))

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_accept_invitation(request, *args, **kwargs):
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group:
        messages.error(request, _("Puny human, you already have a team!"))
        TeamQuestInvitation.objects.filter(to_user=user).delete()
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    invitation = TeamQuestInvitation.objects.filter(id=kwargs['invitation_id'])
    if not invitation.count():
        messages.error(request, _("Puny human, that is not a valid invitation!"))
    invitation = invitation[0]
    new_group = invitation.from_group

    if new_group.is_full():
        messages.error(request, _("Sorry, that team is already full."))
        invitation.delete()
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    new_group.add_user(user)
    messages.success(request,
        _("You have successfully joined the team %(gn)s!")
        % {'gn': new_group.name})

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_decline_invitation(request, *args, **kwargs):
    pass


@login_required
def setup_request(request, *args, **kwargs):
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group:
        messages.error(request, _("Puny human, you already have a team!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    form = RequestToJoinForm(request.POST)
    if form.is_valid():
        requested_group = form.cleaned_data['to_group']

        if TeamQuestInvitationRequest.objects.filter(from_user=user, to_group=requested_group).count():
            messages.error(request, _("Puny human, you already requested to join %(gn)s. Be patient!") % {'gn': requested_group.name})
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

        if requested_group.users.all().count() > 3:
            messages.error(request, _("The team you requested to join is full."))
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

        TeamQuestInvitationRequest.objects.create(to_group=requested_group, from_user=user)
        messages.success(request, _("You have sent a request to join %(gn)s!") % {'gn': requested_group.name})

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_accept_request(request, *args, **kwargs):
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group is None or not user.is_group_owner():
        messages.error(request, _("Puny human, you are not able to accept requests from other players!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    request_to_join = TeamQuestInvitationRequest.objects.filter(id=kwargs['request_id'])
    if not request_to_join.count():
        messages.error(request, _("Puny human, that is not a valid request!"))
    request_to_join = request_to_join[0]
    new_user = request_to_join.from_user

    if group.is_full():
        messages.error(request, _("Sorry, your team is already full."))
        request_to_join.delete()
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    group.add_user(new_user)
    request_to_join.delete()
    messages.success(request, _("You have successfully added %(pn)s to your team!") % {'pn': new_user.nickname})

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_decline_request(request, *args, **kwargs):
    pass


@login_required
def setup_leave(request):
    quest = TeamQuestGame.get_current()
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    if group is None:
        messages.error(request, _("Puny human, you do not have a team to leave!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    if quest is not None:
        if TeamQuestStatus.objects.filter(quest=quest, group=group).count():
            messages.error(request, _("Puny human, you cannot leave your team while venturing in a quest!"))
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    messages.success(request, _("You have left the team %(gn)s. Good luck in your adventures!") % {'gn': group.name})
    group.remove_user(user)

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


@login_required
def setup_kick(request, *args, **kwargs):
    quest = TeamQuestGame.get_current()
    user = request.user.get_profile().get_extension(TeamQuestUser)
    group = user.group
    kicked_user = TeamQuestUser.objects.get(id=kwargs['user_id'])
    if group is None or not user.is_group_owner():
        messages.error(request, _("Puny human, you do not have the rights to kick a player!"))
        return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    if quest is not None:
        if TeamQuestStatus.objects.filter(quest=quest, group=group).count():
            messages.error(request, _("Puny human, you can not kick a team member while venturing in a quest!"))
            return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))

    messages.success(request, _("You have exiled %(pn)s from the realm of your team.") % {'pn': kicked_user.nickname})
    group.remove_user(kicked_user)

    return HttpResponseRedirect(reverse('team_hub_view', args=[user.id]))


class TeamQuestIndexView(ListView):
    model = TeamQuestStatus
    context_object_name = 'status'
    template_name = 'teamquest/index.html'

    def get_context_data(self, **kwargs):
        context = super(TeamQuestIndexView, self).get_context_data(**kwargs)
        quest = TeamQuestGame.get_current()
        quest_user = self.request.user.get_profile().get_extension(TeamQuestUser)
        status = None

        if quest and quest_user.group:
            status, created = TeamQuestStatus.get_or_create(quest=quest, group=quest_user.group)
            context['levels'] = status.levels.all()

        context['status'] = status
        context['quest'] = quest
        context['group'] = quest_user.group

        return context

    def post(self, request, **kwargs):
        quest = TeamQuestGame.get_current()
        quest_user = request.user.get_profile().get_extension(TeamQuestUser)
        status = TeamQuestStatus.objects.get(quest=quest, group=quest_user.group)

        for level in status.levels.all():
            for question in level.questions.all():
                answer = request.POST.get('form' + str(question.index))

                if answer is None:
                    continue

                if answer != str(question.question.answer):
                    messages.error(request, _('Wrong answer!'))
                    return HttpResponseRedirect(reverse('teamquest_index_view') + '#stage' + str(level.level.index))

                if question.is_answered():
                    messages.error(request, _("Puny human, don't try to cheat!"))
                    return HttpResponseRedirect(reverse('teamquest_index_view') + '#stage' + str(level.level.index))

                question.answer()
                quest_user.score(amount=level.level.points_per_question)

                if question.level.questions.all().count() == 1:
                    level.finish()
                    messages.success(request,
                        _('Congratulations! You have completed this quest on position #%(fp)d!')
                        % {'fp': level.finish_position})
                    if level.level.bonus and level.finish_position == 1:
                        messages.success(request,
                            _('For being the first to complete this quest, your team is awarded %(lb)d experience points.')
                            % {'lb': level.level.bonus})
                        quest_user.score(amount=level.level.bonus)

                else:

                    if level.completed:
                        level.finish()
                        messages.success(request,
                            _('Congratulations! You have completed this level on position #%(fp)d!')
                            % {'fp': level.finish_position})
                        if level.level.bonus and level.finish_position == 1:
                            messages.success(request,
                                _('For being the first to complete this level, your team is awarded %(lb)d experience points.')
                                % {'lb': level.level.bonus})
                            quest_user.score(amount=level.level.bonus)

                    other_questions = TeamQuestQuestion.objects.filter(level=question.level, state='A')
                    messages.success(request,
                        _('Correct answer! Your team is awarded %(pt)d experience  points.')
                        % {'pt': level.level.points_per_question})
                    if other_questions.count() > 1:
                        messages.success(request,
                            _('You unlocked a question on Level %(in)d!')
                            % {'in': level.next_level.level.index})
                        return HttpResponseRedirect(reverse('teamquest_index_view') + '#stage' + str(level.next_level.level.index))

                return HttpResponseRedirect(reverse('teamquest_index_view') + '#stage' + str(level.level.index))


index = login_required(TeamQuestIndexView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    quest_user = user.get_profile().get_extension(TeamQuestUser)
    quest = TeamQuestGame.get_current()

    group = quest_user.group
    status = None
    status = TeamQuestStatus.objects.filter(group=group, quest=quest)
    if status.count():
        status = status[0]
        progress = status.progress * 1.0 / quest.total_points * 100
    else:
        progress = 0
        status = None

    return render_to_string('teamquest/sidebar.html',
                            {'quest': quest, 'tquser': quest_user,
                             'group': quest_user.group, 'status': status,
                             'progress': progress,
                             })

register_sidebar_block('teamquest', sidebar_widget)
