import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.config.models import Setting
from wouso.core.user.models import UserProfile
from wouso.core.artifacts.models import Artifact
from wouso.core.qpool.models import Schedule, Question, Tag, Category
from wouso.core.qpool import get_questions_with_category
from wouso.interface.cpanel.models import Customization
from wouso.utils.import_questions import import_from_file
from forms import QuestionForm


@login_required
def dashboard(request):

    future_questions = Schedule.objects.filter(day__gte=datetime.datetime.now())
    nr_future_questions = len(future_questions)

    questions = Question.objects.all()
    nr_questions = len(questions)

    return render_to_response('cpanel/index.html',
                              {'nr_future_questions' : nr_future_questions,
                               'nr_questions' : nr_questions, 'module': 'home'},
                              context_instance=RequestContext(request))

@login_required
def customization(request):
    customization = Customization()

    if request.method == "POST":
        for s in customization.props():
            val = request.POST.get(s.name, '')
            s.set_value(val)

    return render_to_response('cpanel/customization.html',
                              {'settings': customization,
                               'module': 'custom'},
                              context_instance=RequestContext(request))

@login_required
def qpool_home(request, cat=None):
    CATEGORIES = (('Qotd', 'qotd'), ('Challenge', 'challenge'), ('Quest', 'quest'))
    if cat is None:
        cat = 'qotd'

    questions = get_questions_with_category(str(cat), endorsed_only=False)
    if cat == 'qotd':
        questions = questions.order_by('schedule__day')

    return render_to_response('cpanel/qpool_home.html',
                              {'questions': questions,
                               'categs': CATEGORIES,
                               'cat': cat,
                               'module': 'qpool',
                               'today': str(datetime.date.today())},
                              context_instance=RequestContext(request))

def question_edit(request, id):
    question = get_object_or_404(Question, pk=id)

    form = None
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

    return render_to_response('cpanel/question_edit.html',
                              {'question': question,
                               'form': form,
                               'module': 'qpool'},
                              context_instance=RequestContext(request))

def question_switch(request, id):
    question = get_object_or_404(Question, pk=id)

    question.active = not question.active
    question.save()

    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

def qotd_schedule(request):
    Schedule.auttomatic()
    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

@login_required
def importer(request):
    categories = Category.objects.all()
    return render_to_response('cpanel/importer.html',
                           {'categories': categories,
                            'module': 'qpool_import'},
                           context_instance=RequestContext(request))

@login_required
def import_from_upload(request):

    cat = request.POST['category']

    category = Category.objects.filter(name=cat)[0]
    import_from_file(request.FILES['file'], endorsed_by=request.user, category=category)
    return render_to_response('cpanel/imported.html',
                              context_instance=RequestContext(request))

@login_required
def artifactset(request, id):
    profile = get_object_or_404(UserProfile, pk=id)
    artifacts = Artifact.objects.all()

    if request.method == "POST":
        artifact = get_object_or_404(Artifact, pk=request.POST.get('artifact', 0))
        profile.artifacts.add(artifact)

    return render_to_response('cpanel/artifactset.html',
                              {'to': profile,
                               'artifacts': artifacts},
                              context_instance=RequestContext(request))
