import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from wouso.core.config.models import Setting
from wouso.core.user.models import UserProfile
from wouso.core.artifacts.models import Artifact
from wouso.core.qpool.models import Schedule, Question
from wouso.core.qpool.models import Tag
from wouso.interface import render_response
from wouso.interface.cpanel.models import Customization
from wouso.utils.import_questions import import_from_file



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
def importer(request):
    tags = Tag.objects.all()
    return render_response('cpanel/importer.html', request,
                           {'tags': tags,
                            'len': len(tags)})

@login_required
def import_from_upload(request):

    selected = request.POST.getlist('tags')

    tags = [Tag.objects.filter(name=tag)[0] for tag in selected]
    import_from_file(request.FILES['file'], request.user, tags)
    return render_response('cpanel/importer.html', request)

@login_required
def artifactset(request, id):
    profile = get_object_or_404(UserProfile, pk=id)
    artifacts = Artifact.objects.all()

    if request.method == "POST":
        artifact = get_object_or_404(Artifact, pk=request.POST.get('artifact', 0))
        profile.artifacts.add(artifact)

    return render_response('cpanel/artifactset.html', request,
                           {'to': profile, 'artifacts': artifacts})