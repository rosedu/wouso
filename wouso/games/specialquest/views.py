from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from wouso.interface import render_string
from models import SpecialQuestUser, SpecialQuestTask


@login_required
def index(request):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    tasks = SpecialQuestTask.objects.all()
    today = date.today()
    tasks_done = [t for t in tasks if t in user.done_tasks.all()]
    tasks_not_done = [t for t in tasks if t not in user.done_tasks.all()]
    tasks_not_done = [(t, (t.end_date - today).days + 1) for t in tasks_not_done]

    return render_to_response('specialquest/index.html',
                    {'tasks_done': tasks_done, 'tasks_not_done': tasks_not_done},
                    context_instance=RequestContext(request))

def task(request, task_id):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    t = get_object_or_404(SpecialQuestTask, pk=task_id)
    done = (t in user.done_tasks.all())
    days_left = (t.end_date - date.today()).days
    days_left += 1 # including current day

    return render_to_response('specialquest/task.html',
                    {'task': t, 'done': done, 'days_left': days_left},
                    context_instance=RequestContext(request))

def sidebar_widget(request):
    user = request.user.get_profile().get_extension(SpecialQuestUser)
    tasks = SpecialQuestTask.objects.all()
    today = date.today()
    tasks = [t for t in tasks if t not in user.done_tasks.all()
                    and (t.end_date - today).days <= 0]

    return render_string('specialquest/sidebar.html', {'not_done': len(tasks)})

def header_link(request):
    profile = request.user.get_profile()
    if not profile:
        return ''
    user = profile.get_extension(SpecialQuestUser)
    tasks = SpecialQuestTask.objects.all()
    today = date.today()
    tasks = [t for t in tasks if t not in user.done_tasks.all()
                    and (t.end_date - today).days <= 0]

    count = len(tasks)

    link = '<a href="'+ reverse('wouso.games.specialquest.views.index') +'">' + _('Tasks') + '</a>'

    if count > 0:
        link += '<span class="unread-count">%d</span>' % count
    return link
