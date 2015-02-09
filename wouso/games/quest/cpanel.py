# views for wouso cpanel
import datetime
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.views.generic import ListView

from wouso.core import scoring
from wouso.core.qpool import get_questions_with_category
from wouso.core.user.models import Player
from models import Quest, QuestUser, FinalQuest, QuestGame
from forms import QuestCpanel


class QuestHomeView(ListView):
    model = Quest
    template_name = 'quest/cpanel_home.html'
    context_object_name = 'quests'

    def get_context_data(self, **kwargs):
        context = super(QuestHomeView, self).get_context_data(**kwargs)
        final = QuestGame.get_final()
        context.update({'final': final,
                        'final_checker': settings.FINAL_QUEST_CHECKER_PATH,
                        'module': 'quest'})
        return context

quest_home = permission_required('quest.change_quest')(QuestHomeView.as_view())

@permission_required('quest.change_quest')
def quest_edit(request, id=None):
    if id is not None:
        quest = get_object_or_404(Quest, pk=id)
    else:
        quest = None

    form = QuestCpanel(instance=quest)
    form.fields['questions'].queryset = get_questions_with_category('quest').order_by('-id')

    if request.method == 'POST':
        form = QuestCpanel(request.POST, instance=quest)
        form.fields['questions'].queryset = get_questions_with_category('quest').order_by('-id')
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.games.quest.cpanel.quest_home'))

    return render_to_response('quest/cpanel_quest_edit.html',
                              {'quest': quest,
                               'form': form,
                               'module': 'quest'},
                              context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def quest_sort(request, id):
    quest = get_object_or_404(Quest, pk=id)

    if request.method == 'POST':
        neworder = request.POST.get('order')
        if neworder:
            # convert str to array
            order = [i[1] for i in map(lambda a: a.split('='), neworder.split('&'))]
            quest.reorder(order)
            return HttpResponseRedirect(reverse('wouso.games.quest.cpanel.quest_home'))

    return render_to_response('quest/cpanel_quest_sort.html',
                              {'quest': quest,
                               'module': 'quest'},
                              context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def final_results(request):
    final = QuestGame.get_final()
    if not final:
        return render_to_response('quest/cpanel_final_results.html',
                            context_instance=RequestContext(request))
    levels = final.fetch_levels()
    return render_to_response('quest/cpanel_final_results.html',
                              {'quest': final,
                               'module': 'quest',
                               'levels': levels},
                              context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def final_score(request):
    final = QuestGame.get_final()
    if final:
        final.give_level_bonus()

    return render_to_response('quest/cpanel_final_results.html',
                              {'quest': final, 'done': True},
                            context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def create_finale(request):
    if QuestGame.final_exists():
        fq = QuestGame.get_final()
    else:
        fq = FinalQuest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now())

    return HttpResponseRedirect(reverse('quest_edit', args=(fq.id,)))


@permission_required('quest.change_quest')
def quest_bonus(request, id):
    quest = get_object_or_404(Quest, pk=id)
    quest.give_bonus()
    return redirect('quest_home')

@permission_required('quest.change_quest')
def register_results(request, id):
    quest = get_object_or_404(Quest, pk=id)
    quest.register()
    return redirect('quest_home')
