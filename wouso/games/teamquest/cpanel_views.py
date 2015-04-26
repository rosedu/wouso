from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView

from wouso.games.teamquest.models import TeamQuest


class QuestsView(ListView):
    model = TeamQuest
    context_object_name = 'quests'
    template_name = 'teamquest/cpanel/list_quests.html'


quests = permission_required('config.change_setting')(QuestsView.as_view())
