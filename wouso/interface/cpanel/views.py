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
from forms import QuestionForm, TagsForm


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

# used by qpool and qpool_search
CATEGORIES = (('Qotd', 'qotd'), ('Challenge', 'challenge'), ('Quest', 'quest'))

@login_required
def qpool_home(request, cat=None):
    if cat is None:
        cat = 'qotd'

    questions = get_questions_with_category(str(cat), endorsed_only=False)
    if cat == 'qotd':
        questions = questions.order_by('schedule__day')

    tags = Tag.objects.all().exclude(name__in=['qotd', 'challenge', 'quest'])
    form = TagsForm(tags=tags)

    return render_to_response('cpanel/qpool_home.html',
                              {'questions': questions,
                               'categs': CATEGORIES,
                               'cat': cat,
                               'form': form,
                               'module': 'qpool',
                               'tags': len(tags),
                               'today': str(datetime.date.today())},
                              context_instance=RequestContext(request))

def qpool_search(request):
    query = request.GET.get('q', '')
    if query is not None:
        questions = Question.objects.filter(text__icontains=query)
    else:
        questions = []

    return render_to_response('cpanel/qpool_home.html',
                           {'questions': questions, 'categs': CATEGORIES,
                            'cat': 'search', 'module': 'qpool', 'today': str(datetime.date.today()),
                            'q': query},
                           context_instance=RequestContext(request))

def question_edit(request, id=None):
    if id is not None:
        question = get_object_or_404(Question, pk=id)
    else:
        question = None

    form = None
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

    return render_to_response('cpanel/question_edit.html',
                              {'question': question,
                               'form': form,
                               'module': 'qpool',
                               'categs': CATEGORIES},
                              context_instance=RequestContext(request))

def question_switch(request, id):
    question = get_object_or_404(Question, pk=id)

    question.active = not question.active
    question.save()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.qpool_home')

    return HttpResponseRedirect(go_back)

def question_del(request, id):
    question = get_object_or_404(Question, pk=id)

    question.delete()

    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

def qotd_schedule(request):
    Schedule.automatic()
    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

def set_active_categories(request):
    if request.method == 'POST':
        tags = Tag.objects.all().exclude(name__in=['qotd', 'quest', 'challenge'])
        tdict = {}
        for tag in tags:
            tdict[tag.name] = [tag, False]
        for item in request.POST.keys():
            if item in tdict:
                tdict[item][0].set_active()
                tdict[item][1] = True
        for tag in tdict:
            if tdict[tag][1] is False:
                tdict[tag][0].set_inactive()
        return qpool_home(request, 'challenge')

@login_required
def importer(request):
    categories = Category.objects.all()
    return render_to_response('cpanel/importer.html',
                           {'categories': categories,
                            'module': 'qpool'},
                           context_instance=RequestContext(request))

@login_required
def import_from_upload(request):
    # TODO: use form
    cat = request.POST.get('category', None)

    category = Category.objects.filter(name=cat)[0]
    infile = request.FILES.get('file', None)
    if not infile:
        return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.importer'))

    nr = import_from_file(infile, endorsed_by=request.user, category=category)
    return render_to_response('cpanel/imported.html', {'module': 'qpool', 'nr': nr},
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

@login_required
def groupset(request, id):
    profile = get_object_or_404(UserProfile, pk=id)

    from django.forms import ModelForm

    class GForm(ModelForm):
        class Meta:
            model = UserProfile
            fields = ('groups',)

    if request.method == 'POST':
        form = GForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = GForm(instance=profile)

    return render_to_response('cpanel/groupset.html',
                              {'to': profile,
                               'form': form},
                              context_instance=RequestContext(request))
