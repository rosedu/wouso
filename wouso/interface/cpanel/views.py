import datetime
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django import forms
from django.http import  HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from wouso.core.user.models import Player, PlayerGroup, Race
from wouso.core.magic.models import Artifact, ArtifactGroup
from wouso.core.qpool.models import Schedule, Question, Tag, Category
from wouso.core.qpool import get_questions_with_category
from wouso.core.god import God
from wouso.core import scoring
from wouso.interface.cpanel.models import Customization, Switchboard, GamesSwitchboard
from wouso.interface.apps.qproposal import QUEST_GOLD, CHALLENGE_GOLD, QOTD_GOLD
from wouso.utils.import_questions import import_from_file
from forms import QuestionForm, TagsForm, UserForm


@login_required
def dashboard(request):
    from wouso.games.quest.models import Quest, QuestGame
    from django import get_version
    from wouso.settings import WOUSO_VERSION

    future_questions = Schedule.objects.filter(day__gte=datetime.datetime.now())
    nr_future_questions = len(future_questions)

    questions = Question.objects.all()
    nr_questions = len(questions)
    active_quest = QuestGame().get_current()
    total_quests = Quest.objects.all().count()

    # artifacts
    artifact_groups = ArtifactGroup.objects.all()

    # admins
    staff_group, new = auth.Group.objects.get_or_create(name='Staff')

    return render_to_response('cpanel/index.html',
                              {'nr_future_questions' : nr_future_questions,
                               'nr_questions' : nr_questions,
                               'active_quest': active_quest,
                               'total_quests': total_quests,
                               'module': 'home',
                               'artifact_groups': artifact_groups,
                               'django_version': get_version(),
                               'wouso_version': WOUSO_VERSION,
                               'staff': staff_group,
                               },
                              context_instance=RequestContext(request))

@login_required
def customization(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('dashboard'))

    customization = Customization()
    switchboard = Switchboard()

    if request.method == "POST":
        for group in (customization, switchboard):
            for s in group.props():
                val = request.POST.get(s.name, '')
                s.set_value(val)

    return render_to_response('cpanel/customization.html',
                              {'settings': (customization, switchboard),
                               'module': 'custom'},
                              context_instance=RequestContext(request))

@login_required
def games(request):
    switchboard = GamesSwitchboard()

    if request.method == "POST":
        for group in (switchboard,):
            for s in group.props():
                val = request.POST.get(s.name, '')
                s.set_value(val)

    return render_to_response('cpanel/customization.html',
                              {'settings': (switchboard,),
                               'module': 'games'},
                              context_instance=RequestContext(request))

# TODO: gather categories from db.
# used by qpool and qpool_search
CATEGORIES = (('Qotd', 'qotd'), ('Challenge', 'challenge'), ('Quest', 'quest'), ('Proposed', 'proposed'),
    ('Workshop', 'workshop'))

@login_required
def qpool_home(request, cat=None, page=u'1', tag=None):
    if cat is None:
        cat = 'qotd'

    questions = get_questions_with_category(str(cat), active_only=False, endorsed_only=False)
    if tag:
        tag = get_object_or_404(Tag, pk=tag, category__name=cat)
        questions = questions.filter(tags=tag)

    if cat == 'qotd':
        questions = questions.order_by('schedule__day')


    tags = Tag.objects.all().exclude(name__in=['qotd', 'challenge', 'quest'])
    form = TagsForm(tags=tags)

    paginator = Paginator(questions, 15)
    try:
        q_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        q_page = paginator.page(paginator.num_pages)

    return render_to_response('cpanel/qpool_home.html',
                              {'q_page': q_page,
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

@login_required
def question_edit(request, id=None):
    if id is not None:
        question = get_object_or_404(Question, pk=id)
    else:
        question = None

    categs = [(c.name.capitalize(), c.name) for c in Category.objects.all()]

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            newq = form.save()
            if (newq.endorsed_by is None):
                newq.endorsed_by = request.user
                newq.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home', args = (newq.category.name,)))
    else:
        show_users = False
        if question:
            if question.category:
                if question.category.name == 'proposed':
                    show_users = True

        form = QuestionForm(instance=question, users=show_users)

    return render_to_response('cpanel/question_edit.html',
                              {'question': question,
                               'form': form,
                               'module': 'qpool',
                               'categs': categs},
                              context_instance=RequestContext(request))

@login_required
def question_switch(request, id):
    question = get_object_or_404(Question, pk=id)

    # qproposal - endorse part
    proposed_cat = Category.objects.filter(name='proposed')[0]
    if question.category == proposed_cat:
        if not question.endorsed_by:
            player = question.proposed_by.get_profile()
            staff_user = request.user
            question.endorsed_by = staff_user
            question.save()
            amount = 0
            for tag in question.tags.all():
                if tag.name == 'qotd':
                    amount = QOTD_GOLD
                elif tag.name == 'challenge':
                    amount = CHALLENGE_GOLD
                elif tag.name == 'quest':
                    amount = QUEST_GOLD
            scoring.score(player, None, 'bonus-gold', external_id=staff_user.id, gold=amount)

    # regular activation of question
    else:
        question.active = not question.active
        question.save()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.qpool_home')

    return HttpResponseRedirect(go_back)

@login_required
def remove_all(request, cat=None):
    if cat is None:
        return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

    category = Category.objects.filter(name=cat)[0]
    questions = Question.objects.filter(category=category)

    for q in questions:
        q.delete()

    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

@login_required
def question_del(request, id):
    question = get_object_or_404(Question, pk=id)

    question.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.qpool_home')

    return HttpResponseRedirect(go_back)

@login_required
def qotd_schedule(request):
    Schedule.automatic()
    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.qpool_home'))

@login_required
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
    categories = Category.objects.all().exclude(name='proposed')
    tags = Tag.objects.all().exclude(name__in=['qotd', 'challenge', 'quest'])

    return render_to_response('cpanel/importer.html',
                           {'categories': categories,
                            'tags': tags,
                            'module': 'qpool'},
                           context_instance=RequestContext(request))

@login_required
def import_from_upload(request):
    # TODO: use form
    cat = request.POST.get('category', None)
    tags = request.POST.getlist('tags')

    all_active = False
    if request.POST.has_key('all_active'):
        all_active = True
        endorsed_by = request.user
    else:
        endorsed_by = None

    if cat is not None:
        category = Category.objects.get(name=cat)
    else:
        category = None
    tags = [Tag.objects.filter(name=tag)[0] for tag in tags]
    infile = request.FILES.get('file', None)
    if not infile:
        return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.importer'))


    nr = import_from_file(infile, proposed_by=request.user, endorsed_by=endorsed_by, category=category, tags=tags, all_active=all_active)
    return render_to_response('cpanel/imported.html', {'module': 'qpool', 'nr': nr},
                              context_instance=RequestContext(request))

@login_required
def artifactset(request, id):
    profile = get_object_or_404(Player, pk=id)
    artifacts = Artifact.objects.all()

    if request.method == "POST":
        artifact = get_object_or_404(Artifact, pk=request.POST.get('artifact', 0))
        amount = int(request.POST.get('amount', 1))
        profile.give_modifier(artifact.name, amount)

    return render_to_response('cpanel/artifactset.html',
                              {'to': profile,
                               'artifacts': artifacts},
                              context_instance=RequestContext(request))
@login_required
def artifact_home(request, group=None):
    if group is None:
        group = 'Default'

    group = get_object_or_404(ArtifactGroup, name=group)
    artifacts = group.artifact_set.all()
    modifiers = God.get_all_modifiers()

    return render_to_response('cpanel/artifact_home.html',
                              {'groups': ArtifactGroup.objects.all(),
                               'artifacts': artifacts,
                               'module': 'artifacts',
                               'group': group,
                               'modifiers': modifiers,
                               },
                              context_instance=RequestContext(request))

@login_required
def artifact_edit(request, id=None):
    if id is not None:
        instance = get_object_or_404(Artifact, pk=id)
    else:
        instance = None

    from django.forms import ModelForm
    import os.path

    class AForm(ModelForm):
        class Meta:
            model = Artifact

    if request.method == "POST":
        form = AForm(request.POST, instance=instance)
        if form.is_valid():
            # Upload file, if necessary
            image = request.FILES.get('image', False)
            if image:
                path = os.path.join(settings.MEDIA_ARTIFACTS_DIR, image.name)
                with open(path, 'wb+') as fout:
                    for chunk in image.chunks():
                        fout.write(chunk)
            instance = form.save()
            if image:
                instance.image = image
                instance.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.artifact_home'))
    else:
        form = AForm(instance=instance)

    return render_to_response('cpanel/artifact_edit.html',
                            {'form': form, 'instance': instance},
                              context_instance=RequestContext(request))

@login_required
def artifact_del(request, id):
    artifact = get_object_or_404(Artifact, pk=id)

    artifact.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.artifact_home')

    return HttpResponseRedirect(go_back)

@login_required
def tag_questions(request):
    class TagForm(forms.Form):
        questions = forms.MultipleChoiceField(choices=[(q.pk, q.text) for q in Question.objects.all()])
        tag = forms.ChoiceField(choices=[(t.pk, t.name) for t in Tag.objects.all().exclude(name__in=['qotd', 'quest', 'challenge'])])

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            q_pks = form.cleaned_data['questions']
            tag_pk =  form.cleaned_data['tag']
            tag = Tag.objects.get(pk=tag_pk)
            for pk in q_pks:
                q = Question.objects.get(pk=pk)
                q.tags.add(tag)
                q.save()
            return render_to_response('cpanel/tagged.html',
                                    {'nr': len(q_pks)},
                                      context_instance=RequestContext(request))
    else:
        form = TagForm()

    return render_to_response('cpanel/tag_questions.html',
                            {'form': form},
                              context_instance=RequestContext(request))

@login_required
def groupset(request, id):
    profile = get_object_or_404(Player, pk=id)

    from django.forms import ModelForm, SelectMultiple

    class GSelect(SelectMultiple):
        def render_option(self, selected_choices, option_value, option_label):
            group = PlayerGroup.objects.get(pk=option_value)
            option_label = u'%s [%s]' % (group, group.name)
            return super(GSelect, self).render_option(selected_choices, option_value, option_label)

    class GForm(ModelForm):
        class Meta:
            model = Player
            fields = ('race',)
            widgets = {'groups': GSelect()}

        group = forms.ChoiceField(choices=[(0, '')] + [(p.id, p) for p in PlayerGroup.objects.all()],
                                initial=profile.group.id if profile.group else '')

    if request.method == 'POST':
        form = GForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # First remove other group
            if profile.group:
                profile.group.players.remove(profile)
            # Then update, if any
            if form.cleaned_data['group'] != '0':
                new_group = get_object_or_404(PlayerGroup, pk=form.cleaned_data['group'])
                new_group.players.add(profile)
    else:
        form = GForm(instance=profile)

    return render_to_response('cpanel/groupset.html',
                              {'to': profile,
                               'form': form},
                              context_instance=RequestContext(request))

@login_required
def stafftoggle(request, id):
    profile = get_object_or_404(Player, pk=id)

    if profile != request.user.get_profile():
        staff_group, new = auth.Group.objects.get_or_create(name='Staff')
        # TODO: fixme
        if staff_group in profile.user.groups.all():
            profile.user.groups.remove(staff_group)
        else:
            profile.user.groups.add(staff_group)

    return HttpResponseRedirect(reverse('player_profile', args=(id,)))

@login_required
def players(request):
    from wouso.core.scoring.models import History
    from wouso.interface.activity.models import Activity
    def qotdc(self):
        return History.objects.filter(user=self, game__name='QotdGame').count()
    def ac(self):
        return Activity.get_player_activity(self).count()
    def cc(self):
        return History.objects.filter(user=self, game__name='ChallengeGame').count()
    Player.qotd_count = qotdc
    Player.activity_count = ac
    Player.chall_count = cc
    all = Player.objects.all().order_by('-user__date_joined')

    return render_to_response('cpanel/players.html', dict(players=all), context_instance=RequestContext(request))

@login_required
def add_player(request):
    form = UserForm()
    if request.method == "POST":
        user = UserForm(data = request.POST)
        if user.is_valid():
            user.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.players'))
        else:
            form = user
    return render_to_response('cpanel/add_player.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def races_groups(request):
    return render_to_response('cpanel/races_groups.html', {'races': Race.objects.all()},
        context_instance=RequestContext(request)
    )


# 'I am lazy' hack comes in
import sys
import types
except_functions = ('login_required', 'permission_required','render_to_response', 'get_object_or_404',
    'reverse', 'get_questions_with_category', 'get_themes', 'import_from_file')
module = sys.modules[__name__].__dict__
for i in module.keys():
    if isinstance(module[i], types.FunctionType):
        if i in except_functions:
            continue
        module[i] = permission_required('config.change_setting')(module[i])
