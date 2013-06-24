# views for wouso cpanel
import datetime
from django.contrib.auth.decorators import permission_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from wouso.core import scoring
from wouso.core.qpool import get_questions_with_category
from wouso.core.scoring import History
from wouso.core.user.models import Player
from models import Quest, QuestUser, FinalQuest, QuestGame
from forms import QuestCpanel


@permission_required('quest.change_quest')
def quest_home(request):
    quests = Quest.objects.all()
    final = QuestGame.get_final()

    return render_to_response('quest/cpanel_home.html',
                              {'quests': quests,
                               'final': final,
                               'final_checker': settings.FINAL_QUEST_CHECKER_PATH,
                               'module': 'quest'},
                              context_instance=RequestContext(request))

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

    # fetch levels
    levels = []
    for level in xrange(len(final.levels) + 1):
        level_data = {'id': level, 'users': []}
        for user in QuestUser.objects.filter(current_quest=final, current_level=level):
            # Check finalquest bonus amount
            amount = History.objects.filter(user=user.user, formula__name='finalquest-ok').aggregate(sum=Sum('amount'))['sum']
            user.amount = amount
            level_data['users'].append(user)
        levels.append(level_data)

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
def quest_bonus(request, quest):
    quest = get_object_or_404(Quest, pk=quest)

    # TODO: move logic to models
    for i, r in enumerate(quest.top_results()):
        player = r.user.get_extension(Player)
        scoring.score(player, QuestGame, 'quest-finish-bonus', position=i + 1, external_id=quest.id)

    return redirect('quest_home')

@permission_required('quest.change_quest')
def register_results(request, id):
    quest = get_object_or_404(Quest, pk=id)
    if not quest.is_active:
        for user in quest.questuser_set.all():
            user.register_quest_result()
        quest.registered = True
        quest.save()
    return redirect('quest_home')
