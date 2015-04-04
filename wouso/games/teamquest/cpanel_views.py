from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView

from models import TeamQuest


class QuestsView(ListView):
    model = TeamQuest
    template_name = 'teamquest/quests.html'
    context_object_name = 'quests'


quests = permission_required('config.change_setting')(QuestsView.as_view())
