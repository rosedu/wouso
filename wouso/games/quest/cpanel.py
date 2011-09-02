# views for wouso cpanel
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wouso.interface import render_response
from wouso.core.qpool import get_questions_with_category
from models import Quest
from forms import QuestCpanel

def quest_home(request):
    quests = Quest.objects.all()

    return render_response('quest/cpanel_home.html', request,
                           {'quests': quests})

def quest_edit(request, id=None):
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

    return render_response('quest/cpanel_quest_edit.html', request,
                           {'quest': quest, 'form': form})

def quest_sort(request, id):
    quest = get_object_or_404(Quest, pk=id)

    if request.method == 'POST':
        neworder = request.POST.get('order')
        if neworder:
            # convert str to array
            order = [i[1] for i in map(lambda a: a.split('='), neworder.split('&'))]
            quest.reorder(order)
            return HttpResponseRedirect(reverse('wouso.games.quest.cpanel.quest_home'))

    return render_response('quest/cpanel_quest_sort.html', request,
                           {'quest': quest})
