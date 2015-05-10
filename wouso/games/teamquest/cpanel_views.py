from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse_lazy

from wouso.games.teamquest.models import TeamQuest, TeamQuestGroup
from wouso.games.teamquest.forms import AddTeamQuest


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


class AddTeamQuestView(CreateView):
    form_class = AddTeamQuest
    success_url = reverse_lazy('teamquest_home')
    template_name = 'teamquest/cpanel/add_teamquest.html'


add_teamquest = permission_required('config.change_setting')(AddTeamQuestView.as_view())
