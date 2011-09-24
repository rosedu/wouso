# views for wouso cpanel
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.qpool import get_questions_with_category
from models import Quest
from forms import QuestCpanel

@permission_required('quest.change_quest')
def home(request):
    quests = Quest.objects.all()

    return render_to_response('quest/cpanel_home.html',
                              {'quests': quests,
                               'module': 'quest'},
                              context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def edit(request, id=None):
    if id is not None:
        quest = get_object_or_404(Quest, pk=id)
    else:
        quest = None

    form = QuestCpanel(instance=quest)
    form.fields['questions'].queryset = get_questions_with_category('quest')

    if request.method == 'POST':
        form = QuestCpanel(request.POST, instance=quest)
        form.fields['questions'].queryset = get_questions_with_category('quest')
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.games.quest.cpanel.quest_home'))

    return render_to_response('quest/cpanel_quest_edit.html',
                              {'quest': quest,
                               'form': form,
                               'module': 'quest'},
                              context_instance=RequestContext(request))

