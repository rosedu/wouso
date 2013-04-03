import datetime
from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import  permission_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django import forms
from django.http import  HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from wouso.core.decorators import staff_required
from wouso.core.user.models import Player, PlayerGroup, Race
from wouso.core.magic.models import Artifact, ArtifactGroup, Spell
from wouso.core.qpool.models import Schedule, Question, Tag, Category, Answer
from wouso.core.qpool import get_questions_with_category
from wouso.core.god import God
from wouso.core import scoring
from wouso.core.scoring.models import Formula, History, Coin
from wouso.core.signals import addActivity, add_activity
from wouso.core.security.models import Report
from wouso.games.challenge.models import Challenge, Participant
from wouso.interface.apps.messaging.models import Message
from wouso.interface.cpanel.models import Customization, Switchboard, GamesSwitchboard
from wouso.interface.apps.qproposal import QUEST_GOLD, CHALLENGE_GOLD, QOTD_GOLD
from wouso.utils.import_questions import import_from_file
from wouso.middleware.impersonation import ImpersonateMiddleware
from forms import QuestionForm, TagsForm, UserForm, SpellForm, AddTagForm, AnswerForm, EditReportForm
from forms import FormulaForm

@staff_required
def dashboard(request):
    from wouso.games.quest.models import Quest, QuestGame
    from django import get_version
    from wouso.settings import WOUSO_VERSION, DATABASES
    from wouso.core.config.models import Setting

    database = DATABASES['default'].copy()
    database_engine = database['ENGINE'].split('.')[-1]
    database_name = database['NAME']
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

    # wousocron last_run
    last_run = Setting.get('wousocron_lastrun').get_value()
    if last_run == "":
        last_run="wousocron was never run"

    # online members
    oldest = datetime.datetime.now() - datetime.timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest).order_by('-last_seen')

    # number of players which can play
    cp_number = Player.objects.filter(race__can_play=True).count()

    return render_to_response('cpanel/index.html',
                              {'nr_future_questions' : nr_future_questions,
                               'nr_questions' : nr_questions,
                               'active_quest': active_quest,
                               'total_quests': total_quests,
                               'module': 'home',
                               'artifact_groups': artifact_groups,
                               'django_version': get_version(),
                               'wouso_version': WOUSO_VERSION,
                               'database_engine': database_engine,
                               'database_name': database_name,
                               'staff': staff_group,
                               'last_run': last_run,
                               'online_users': online_last10,
                               'cp_number': cp_number,
                               },
                              context_instance=RequestContext(request))

@permission_required('config.change_setting')
def formulas(request):
    formulas = Formula.objects.all()
    return render_to_response('cpanel/formulas_home.html',
                              {'formulas': formulas
                              },
                              context_instance=RequestContext(request))

@permission_required('config.change_setting')
def edit_formula(request, id):
    formula = get_object_or_404(Formula, pk=id)
    if request.method == "POST":
        form = FormulaForm(data=request.POST, instance=formula)
        if form.is_valid():
            form.save()
            return redirect('formulas')
    else:
        form = FormulaForm(instance=formula)
    return render_to_response('cpanel/edit_formula.html',
                              {'form': form},
                              context_instance = RequestContext(request))

@permission_required('config.change_setting')
def formula_delete(request, id):
    formula = get_object_or_404(Formula, pk=id)
    formula.delete()
    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.formulas')
    return HttpResponseRedirect(go_back)

@permission_required('config.change_setting')
def add_formula(request):
    form = FormulaForm()
    if request.method == "POST":
        formula = FormulaForm(data = request.POST)
        if formula.is_valid():
            formula.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.formulas'))
        else:
            form = formula
    return render_to_response('cpanel/add_formula.html',
                              {'form': form},
                              context_instance=RequestContext(request))

@permission_required('config.change_setting')
def spells(request):
    spells = Spell.objects.all()
    spells_bought = 0
    spells_used = 0
    spells_expired = 0
    spells_cleaned = 0
    for p in spells:
        spells_bought = spells_bought + p.history_bought()
        spells_used = spells_used + p.history_used()
        spells_expired = spells_expired + p.history_expired()
        spells_cleaned = spells_cleaned + p.history_cleaned()
    return render_to_response('cpanel/spells_home.html',
                              {'spells' : spells,
                               'spells_bought' : spells_bought,
                               'spells_used' : spells_used,
                               'spells_expired' : spells_expired,
                               'spells_cleaned' : spells_cleaned,
                               'module': 'spells',
                              },
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def edit_spell(request, id):
    spell = get_object_or_404(Spell, pk=id)
    if request.method == "POST":
        form = SpellForm(data = request.POST, instance = spell, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.spells'))
    else:
        form = SpellForm(instance=spell)
    return render_to_response('cpanel/edit_spell.html', {'form':form, 'module': 'spells'}, context_instance=RequestContext(request))


@permission_required('config.change_setting')
def add_spell(request):
    form = SpellForm()
    if request.method == "POST":
        spell = SpellForm(data=request.POST, files=request.FILES)
        if spell.is_valid():
            spell.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.spells'))
        else:
            form = spell
    return render_to_response('cpanel/add_spell.html', {'form': form, 'module': 'spells'}, context_instance=RequestContext(request))


@permission_required('config.change_setting')
def spell_delete(request, id):
    spell = get_object_or_404(Spell, pk=id)

    spell.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.spells')

    return HttpResponseRedirect(go_back)


@permission_required('config.change_setting')
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


@permission_required('config.change_setting')
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


@permission_required('config.change_setting')
def qpool_home(request, cat='qotd', page=u'1', tag=None):
    categories = Category.objects.all()


    qs = get_questions_with_category(str(cat), active_only=False, endorsed_only=False)
    if tag:
        tag = get_object_or_404(Tag, pk=tag, category__name=cat)
        qs = qs.filter(tags=tag)

    if request.GET.get('q'):
        # This is a search query
        query = request.GET.get('q')
        qs = qs.filter(text__icontains=query)
    else:
        query = ''

    category = get_object_or_404(Category, name=cat)
    session_filter_name = 'tag_filters_%s' % category.name
    tag_filters = request.session.get(session_filter_name, [])
    if request.GET.get('addtagfilter'):
        tag = get_object_or_404(Tag, pk=request.GET.get('addtagfilter'))
        tag_filters.append(tag.id)
    if request.GET.get('remtagfilter'):
        tag = get_object_or_404(Tag, pk=request.GET.get('remtagfilter'))
        if tag.id in tag_filters:
            tag_filters.remove(tag.id)
    request.session[session_filter_name] = tag_filters
    if tag_filters:
        qs = qs.filter(tags__in=tag_filters)

    prop_filter_name = 'prop_filters_%s' % category.name
    prop_filters = request.session.get(prop_filter_name, [])
    if request.GET.get('addpropfilter'):
        prop_filters.append(request.GET.get('addpropfilter'))
    if request.GET.get('rempropfilter'):
        f = request.GET.get('rempropfilter')
        if f in prop_filters:
            prop_filters.remove(f)
    request.session[prop_filter_name] = prop_filters
    if 'active' in prop_filters:
        qs = qs.filter(active=True)

    # Ordering
    if cat == 'qotd':
        qs = qs.order_by('schedule__day')

    # Pagination
    perpage = request.session.get('qpool_perpage', 15)
    if request.GET.get('changeperpage'):
        perpage = int(request.GET.get('changeperpage'))
    request.session['qpool_perpage'] = perpage
    paginator = Paginator(qs, perpage)
    try:
        q_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        q_page = paginator.page(paginator.num_pages)

    return render_to_response('cpanel/qpool_home.html',
                              {'q_page': q_page,
                               'categs': categories,
                               'category': category,
                               'tag_filters': tag_filters,
                               'prop_filters': prop_filters,
                               'cat': cat,
                               'search_query': query,
                               'perpage_options': (15, 50, 100),
                               'module': 'qpool',
                               'today': str(datetime.date.today())},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def qpool_new(request, cat=None):
    form = QuestionForm()
    categs = [(c.name.capitalize(), c.name) for c in Category.objects.all()]
    if request.method == "POST":
        question = QuestionForm(data = request.POST)
        if question.is_valid():
            newq = question.save()
            return redirect('qpool_home', cat=newq.category.name)
        else:
            form = question

    return render_to_response('cpanel/qpool_new.html',
            {'form': form,
             'module': 'qpool',
             'categs': categs},
            context_instance=RequestContext(request)
    )


@permission_required('config.change_setting')
def qpool_add_answer(request, id):
    form = AnswerForm()
    question = get_object_or_404(Question, pk=id)
    if request.method == 'POST':
        answer = AnswerForm(request.POST, instance=question)
        if answer.is_valid():
            answer.save(id=question)
            return redirect('question_edit', id=question.id)
        else:
            form = answer

    return render_to_response('cpanel/add_answer.html',
            {'form': form,
             'question': question,
             'module': 'qpool'},
            context_instance=RequestContext(request)
    )


@permission_required('config.change_setting')
def qpool_edit(request, id=None):
    if id is not None:
        question = get_object_or_404(Question, pk=id)
    else:
        return qpool_new(request)

    categs = [(c.name.capitalize(), c.name) for c in Category.objects.all()]

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            newq = form.save()
            if newq.endorsed_by is None:
                newq.endorsed_by = request.user
                newq.save()
            return redirect('qpool_home', cat = newq.category.name)
        else:
            print "nevalid"
    else:
        show_users = False
        if question:
            if question.category:
                if question.category.name == 'proposed':
                    show_users = True

        form = QuestionForm(instance=question, users=show_users)

    return render_to_response( 'cpanel/qpool_edit.html',
                              {'question': question,
                               'form': form,
                               'module': 'qpool',
                               'categs': categs},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def question_switch(request, id):
    """ Accept a proposed question
    """
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


@permission_required('config.change_setting')
def qpool_remove_all(request, cat=None):
    category = get_object_or_404(Category, name=cat)

    category.question_set.all().delete()

    return redirect('qpool_home', cat=category.name)


@permission_required('config.change_setting')
def qpool_delete(request, id):
    question = get_object_or_404(Question, pk=id)

    question.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.qpool_home')

    return HttpResponseRedirect(go_back)


@permission_required('config.change_setting')
def qpool_delete_answer(request, question_id, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)

    answer.delete()

    return redirect('question_edit', id=question_id)


@permission_required('config.change_setting')
def qotd_schedule(request):
    Schedule.automatic()
    return redirect('qpool_home', cat='qotd')


@permission_required('config.change_setting')
def qpool_set_active_categories(request):
    category = get_object_or_404(Category, name='challenge')
    tags = category.tag_set.all()
    if request.method == 'POST':
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

    form = TagsForm(tags=tags)
    return render_to_response('cpanel/qpool_setactivetags.html',
                        {'form': form, 'tags': tags},
                        context_instance=RequestContext(request)
    )


@permission_required('config.change_setting')
def qpool_importer(request):
    categories = Category.objects.all().exclude(name='proposed')
    tags = Tag.objects.all().exclude(name__in=['qotd', 'challenge', 'quest'])

    return render_to_response('cpanel/importer.html',
                           {'categories': categories,
                            'tags': tags,
                            'module': 'qpool'},
                           context_instance=RequestContext(request))


@permission_required('config.change_setting')
def qpool_import_from_upload(request):
    # TODO: use a form
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
        return redirect('importer')


    nr = import_from_file(infile, proposed_by=request.user, endorsed_by=endorsed_by, category=category, tags=tags, all_active=all_active)
    return render_to_response('cpanel/imported.html', {'module': 'qpool', 'nr': nr, 'category': category},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def qpool_tag_questions(request):
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


@permission_required('config.change_setting')
def qpool_managetags(request):
    tags = Tag.objects.all().order_by('category')

    return render_to_response('cpanel/qpool_managetags.html',
                            {'tags': tags},
                            context_instance=RequestContext(request)
    )


@permission_required('config.change_setting')
def qpool_add_tag(request):
    form = AddTagForm()
    if request.method == "POST":
        tag = AddTagForm(data = request.POST)
        if tag.is_valid():
            tag.save()
            return redirect('qpool_manage_tags')
        else:
            form = tag
    return render_to_response('cpanel/qpool_add_tag.html',
            {'form': form},
            context_instance=RequestContext(request))


@permission_required('config.change_setting')
def qpool_edit_tag(request, tag):
    tag_obj = get_object_or_404(Tag, pk=tag)
    if request.method == "POST":
        form = AddTagForm(data = request.POST, instance = tag_obj)
        if form.is_valid():
            form.save()
            return redirect('qpool_manage_tags')
    else:
        form = AddTagForm(instance=tag_obj)
    return render_to_response('cpanel/qpool_edit_tag.html', {'form':form, 'tags': tag_obj}, context_instance=RequestContext(request))


@permission_required('config.change_setting')
def qpool_delete_tag(request, tag):
    tag_obj = get_object_or_404(Tag, pk=tag)

    tag_obj.delete()

    return redirect('qpool_manage_tags')


@permission_required('config.change_setting')
def qpool_settag(request):
    tag = get_object_or_404(Tag, pk=request.GET.get('tag'))
    qs = request.GET.get('qs', '').split(',')
    qs.remove('')
    qs = map(int, qs)
    queryset = Question.objects.filter(id__in=qs)
    for q in queryset:
        q.tags.add(tag)

    redir = request.META.get('HTTP_REFERER', reverse('qpool_home'))

    return redirect(redir)

@permission_required('config.change_setting')
def qpool_actions(request):
    action = request.GET.get('action', None)
    qs = request.GET.get('qs', '').split(',')
    qs.remove('')
    qs = map(int, qs)
    queryset = Question.objects.filter(id__in=qs)

    if action == 'active':
        for q in queryset:
            q.set_active()
    elif action == 'inactive':
        for q in queryset:
            q.set_active(False)

    redir = request.META.get('HTTP_REFERER', reverse('qpool_home'))

    return redirect(redir)

@permission_required('config.change_setting')
def qpool_export(request, cat):
    category = get_object_or_404(Category, name=cat)
    response = HttpResponse(mimetype='text/txt')
    response['Content-Disposition'] = 'attachment; filename=question_%s_export.txt' % slugify(category.name)

    for q in category.question_set.all():
        response.write(u'? %s\n' % q.text)
        for a in q.answers:
            response.write(u'%s %s\n' % ('+' if a.correct else '-', a.text))
        response.write('\n')

    return response

# End qpool

@permission_required('config.change_setting')
def artifactset(request, id):
    profile = get_object_or_404(Player, pk=id)
    artifacts = Artifact.objects.all()

    if request.method == "POST":
        artifact = get_object_or_404(Artifact, pk=request.POST.get('artifact', 0))
        amount = int(request.POST.get('amount', 1))
        profile.magic.give_modifier(artifact.name, amount)

    return render_to_response('cpanel/artifactset.html',
                              {'to': profile,
                               'artifacts': artifacts},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
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



@permission_required('config.change_setting')
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



@permission_required('config.change_setting')
def artifact_del(request, id):
    artifact = get_object_or_404(Artifact, pk=id)

    artifact.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.artifact_home')

    return HttpResponseRedirect(go_back)


@permission_required('config.change_setting')
def groupset(request, id):
    profile = get_object_or_404(Player, pk=id)

    from django.forms import ModelForm, SelectMultiple

    class GSelect(SelectMultiple):
        def render_option(self, selected_choices, option_value, option_label):
            group = Race.objects.get(pk=option_value)
            option_label = u'%s [%s]' % (group, group.name)
            return super(GSelect, self).render_option(selected_choices, option_value, option_label)

    class GForm(ModelForm):
        class Meta:
            model = Player
            fields = ('race',)

        group = forms.ChoiceField(choices=[(0, '')] + [(p.id, u"%s [%s]" % (p, p.name)) for p in PlayerGroup.objects.filter(owner=None)],
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


@permission_required('config.change_setting')
def stafftoggle(request, id):
    profile = get_object_or_404(Player, pk=id)

    if profile != request.user.get_profile():
        staff_group, new = auth.Group.objects.get_or_create(name='Staff')
        if profile.in_staff_group():
            if staff_group in profile.user.groups.all():
                profile.user.groups.remove(staff_group)
        else:
            profile.user.groups.add(staff_group)

    return HttpResponseRedirect(reverse('player_profile', args=(id,)))


@permission_required('config.change_setting')
def players(request):
    from wouso.interface.activity.models import Activity
    def qotdc(self):
        return History.objects.filter(user=self, game__name='QotdGame').count()
    def ac(self):
        return Activity.get_player_activity(self).count()
    def cc(self):
        return History.objects.filter(user=self, game__name='ChallengeGame').count()
    def inf(self):
        return History.user_coins(user=self)['penalty']

    Player.qotd_count = qotdc
    Player.activity_count = ac
    Player.chall_count = cc
    Player.infraction_points = inf
    all = Player.objects.all().order_by('-user__date_joined')

    return render_to_response('cpanel/players.html', dict(players=all), context_instance=RequestContext(request))


@permission_required('config.change_setting')
def add_player(request):
    form = UserForm()
    if request.method == "POST":
        user = UserForm(data = request.POST)
        if user.is_valid():
            user.instance.set_password(request.POST['password'])
            user.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.players'))
        else:
            form = user
    return render_to_response('cpanel/add_player.html', {'form': form}, context_instance=RequestContext(request))


@permission_required('config.change_setting')
def edit_player(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = UserForm(data = request.POST, instance = user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.players'))
    else:
        form = UserForm(instance=user)
        form.fields['password'].widget.attrs['readonly'] = True
    return render_to_response('cpanel/edit_player.html', {'form':form}, context_instance=RequestContext(request))


@staff_required
def infraction_history(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    inf_list = History.objects.filter(user=user, coin__name='penalty').order_by('-timestamp')
    infractions = {}
    for i in inf_list:
        if i.formula.name=="chall-was-set-up-infraction":
            list = infractions.setdefault(i.formula.name, [])
            list.append( (i, Challenge.objects.get(pk=i.external_id)) )

    return render_to_response('cpanel/view_infractions.html',
            {'infractions':infractions, 'p':user.player_related.get()},
            context_instance=RequestContext(request))


@staff_required
def infraction_recheck(request):
    """ Rerun an infraction check on the current challenge history

        The view should allow for other infraction additions. """
    try:
        inf_list = History.objects.filter(coin__name='penalty',
                formula__name='chall-was-set-up-infraction').delete()
    except:
        pass

    all_participants = Participant.objects.filter(seconds_took__lt=15).exclude(seconds_took=None)
    formula = Formula.objects.get(name='chall-was-set-up-infraction')
    for p in all_participants:
        id = None
        if p.user_from.count():
            if p.user_from.all()[0].status == 'P' and p.user_from.all()[0].winner.id != p.user.id:
                user = p.user.player_ptr
                id = p.user_from.all()[0].id
        if p.user_to.count():
            if p.user_to.all()[0].status == 'P' and p.user_to.all()[0].winner.id != p.user.id:
                user = p.user.player_ptr
                id = p.user_to.all()[0].id
        if id:
           scoring.score(user=user, game=None, formula=formula, external_id=id)
    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.players'))


@staff_required
def infraction_clear(request, user_id, infraction_id):
    History.objects.get(pk=infraction_id).delete()
    return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.infraction_history', args=(user_id,)))


@permission_required('config.change_setting')
def races_groups(request):
    return render_to_response('cpanel/races_groups.html', {'races': Race.objects.all()},
        context_instance=RequestContext(request)
    )


@permission_required('superuser')
def roles(request):
    roles = Group.objects.all()

    return render_to_response('cpanel/roles.html', {'roles': roles},
                              context_instance=RequestContext(request)
    )


@permission_required('superuser')
def roles_update(request, id):
    group = get_object_or_404(Group, pk=id)

    if request.method == 'POST':
        player_id = request.POST['player']
        user = get_object_or_404(Player, pk=player_id).user
        user.groups.add(group)

    return render_to_response('cpanel/roles_update.html', {'role': group},
                              context_instance=RequestContext(request)
    )


@permission_required('superuser')
def roles_update_kick(request, id, player_id):
    group = get_object_or_404(Group, pk=id)
    player = get_object_or_404(Player, pk=player_id)

    if group in player.user.groups.all():
        player.user.groups.remove(group)

    return redirect('roles_update', id=group.id)


@staff_required
def the_bell(request):
    """
    Press the bell: add an phony activity
    """
    player = request.user.get_profile()
    message = ugettext_noop('pressed the bell')
    addActivity.send(sender=None, user_from=player, game=None, message=message)

    return redirect('dashboard')


@staff_required
def reports(request, page=0):
    """
    This page shows the reports
    """

    return render_to_response('cpanel/reports.html',
                    {'reports': Report.objects.all().order_by('-timestamp')},
                    context_instance=RequestContext(request)
    )


@staff_required
def edit_report(request, id):
    report = get_object_or_404(Report, pk=id)

    if request.method == "POST":
        form = EditReportForm(data = request.POST, instance=report)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('wouso.interface.cpanel.views.reports'))
    else:
        reportForm = EditReportForm(instance = report)
        return render_to_response('cpanel/edit_report.html',
                        {'report': report, 'form': reportForm, 'id': id},
                        context_instance=RequestContext(request))


@staff_required
def system_message_group(request, group):
    group = get_object_or_404(PlayerGroup, pk=group)

    if request.method == 'POST':
        text = request.POST['text']
        for p in group.players.all():
            Message.send(sender=None, receiver=p, subject="System message", text=text)
        message = 'Message sent!'
    else:
        message = ''

    return render_to_response('cpanel/system_message_group.html',
                        {'group': group, 'message': message},
                        context_instance=RequestContext(request))


@permission_required('superuser')
def impersonate(request, player_id):
    # TODO: write tests
    player = get_object_or_404(Player, pk=player_id)
    ImpersonateMiddleware.set_impersonation(request, player)
    return redirect('player_profile', id=player.id)


def clean_impersonation(request):
    ImpersonateMiddleware.clear(request)
    return redirect('homepage')


@permission_required('superuser')
def clear_cache(request):
    if request.method == 'POST':
        cache.clear()
        return redirect('dashboard')
    else:
        return render_to_response('cpanel/clear_cache.html', {}, context_instance=RequestContext(request))


class BonusForm(forms.Form):
    amount = forms.IntegerField(initial=0)
    coin = forms.ModelChoiceField(queryset=Coin.objects.all())
    reason = forms.CharField(required=False)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount', None)
        if not amount:
            raise ValidationError('Invalid amount')
        return amount


@permission_required('config.change_setting')
def bonus(request, player_id):
    player = get_object_or_404(Player, pk=player_id)

    if request.method == 'POST':
        form = BonusForm(request.POST)
        if form.is_valid():
            coin, amount = form.cleaned_data['coin'], form.cleaned_data['amount']
            formula = Formula.get('bonus-%s' % coin.name)
            if formula is None:
                messages.error(request, 'No such formula, bonus-%s' % coin.name)
            else:
                scoring.score(player, None, formula, external_id=request.user.get_profile().id, **{coin.name: amount})
                if form.cleaned_data['reason']:
                    add_activity(player, _('received {amount} {coin} bonus for {reason}'), amount=amount, coin=coin, reason=form.cleaned_data['reason'])
                messages.info(request, 'Successfully given bonus')
            return redirect('player_profile', id=player.id)
    else:
        form = BonusForm()

    bonuses = scoring.History.objects.filter(user=player, formula__name__startswith='bonus-').order_by('-timestamp')
    penalties = scoring.History.objects.filter(user=player, formula__name__startswith='penalty-').order_by('-timestamp')

    return render_to_response('cpanel/bonus.html', {'target_player': player, 'form': form, 'bonuses': bonuses, 'penalties': penalties},
        context_instance=RequestContext(request)
    )
