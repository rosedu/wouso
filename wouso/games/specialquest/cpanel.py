# views for wouso cpanel
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.qpool import get_questions_with_category
from models import SpecialQuestTask
from forms import TaskForm

@permission_required('specialquest.change_quest')
def home(request):
    tasks = SpecialQuestTask.objects.all()

    return render_to_response('specialquest/cpanel_home.html',
                              {'tasks': tasks,
                               'module': 'specialquest'},
                              context_instance=RequestContext(request))

@permission_required('quest.change_quest')
def edit(request, id=None):
    if id is not None:
        task = get_object_or_404(SpecialQuestTask, pk=id)
    else:
        task = None

    form = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))

    return render_to_response('specialquest/cpanel_edit.html',
                              {'task': task,
                               'form': form,
                               'module': 'specialquest'},
                              context_instance=RequestContext(request))

@permission_required('specialquest.change_quest')
def delete(request, id=None):
    if id is None:
        return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))
    task = get_object_or_404(SpecialQuestTask, pk=id)
    task.delete()
    return HttpResponseRedirect(reverse('wouso.games.specialquest.cpanel.home'))
