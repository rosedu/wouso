import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from wouso.core.config.models import Setting
from wouso.core.user.models import UserProfile
from wouso.core.artifacts.models import Artifact
from wouso.core.qpool.models import Schedule, Question
from wouso.core.qpool.models import Tag
from wouso.interface import render_response
from wouso.interface.cpanel.models import Customization
from wouso.utils.import_questions import import_from_file
from forms import QuestionForm


@login_required
def dashboard(request):

    future_questions = Schedule.objects.filter(day__gte=datetime.datetime.now())
    nr_future_questions = len(future_questions)

    questions = Question.objects.all()
    nr_questions = len(questions)

    return render_response('cpanel/index.html', request, {'nr_future_questions' : nr_future_questions,
                                                          'nr_questions' : nr_questions})

@login_required
def customization(request):
    customization = Customization()

    if request.method == "POST":
        for s in customization.props():
            val = request.POST.get(s.name, '')
            s.set_value(val)

    return render_response('cpanel/customization.html', request, \
            {'settings': customization}
    )

@login_required
def qpool_home(request):
    questions = Question.objects.all()

    return render_response('cpanel/qpool_home.html', request,
                           {'questions': questions})

def question_edit(request, id):
    question = get_object_or_404(Question, pk=id)

    form = None
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))
        else:
            print form
        print request.POST

    return render_response('cpanel/question_edit.html', request,
                           {'question': question, 'form': form})


@login_required
def importer(request):
    tags = Tag.objects.all()
    return render_response('cpanel/importer.html', request,
                           {'tags': tags,
                            'len': len(tags)})

@login_required
def import_from_upload(request):

    selected = request.POST.getlist('tags')

    tags = [Tag.objects.filter(name=tag)[0] for tag in selected]
    import_from_file(request.FILES['file'], endorsed_by=request.user, tags=tags)
    return render_response('cpanel/imported.html', request)

@login_required
def artifactset(request, id):
    profile = get_object_or_404(UserProfile, pk=id)
    artifacts = Artifact.objects.all()

    if request.method == "POST":
        artifact = get_object_or_404(Artifact, pk=request.POST.get('artifact', 0))
        profile.artifacts.add(artifact)

    return render_response('cpanel/artifactset.html', request,
                           {'to': profile, 'artifacts': artifacts})