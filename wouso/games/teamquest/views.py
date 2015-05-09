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
