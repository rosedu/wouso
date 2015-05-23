from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, TemplateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response

from wouso.games.teamquest.models import TeamQuest, TeamQuestGroup, TeamQuestQuestion
from wouso.games.teamquest.forms import AddTeamQuestForm


class QuestsView(ListView):
    model = TeamQuest
    context_object_name = 'quests'
    template_name = 'teamquest/cpanel/list_quests.html'


quests = permission_required('config.change_setting')(QuestsView.as_view())


class GroupsView(ListView):
    model = TeamQuestGroup
    context_object_name = 'groups'
    template_name = 'teamquest/cpanel/list_groups.html'


groups = permission_required('config.change_setting')(GroupsView.as_view())


class DeleteTeamQuestView(DeleteView):
    model = TeamQuest
    success_url = reverse_lazy('teamquest_home')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_teamquest = permission_required('config.change_setting')(
    DeleteTeamQuestView.as_view())


class AddTeamQuestView(TemplateView):
    template_name = 'teamquest/cpanel/add_teamquest.html'

    def get_context_data(self, **kwargs):
        context = super(AddTeamQuestView, self).get_context_data(**kwargs)
        context['form'] = AddTeamQuestForm()
        return context


add_teamquest = permission_required('config.change_setting')(AddTeamQuestView.as_view())


# @login_required
# def add_teamquestquestions(request):
#     n = request.POST['number_of_levels']
#     form = AddTeamQuestLevelForm(number_of_levels=n)
#     return render_to_response('teamquest/cpanel/add_teamquestquestions.html', {'form': form})
