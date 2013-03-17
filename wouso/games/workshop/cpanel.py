from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.views.generic import ListView

from models import WorkshopGame, Semigroup, Schedule, DAY_CHOICES, Answer
from wouso.core.decorators import staff_required
from wouso.core.user.models import Player
from wouso.games.workshop.models import Workshop, Assessment, Review

class SCForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('name', 'start_date', 'end_date', 'count')


class AGForm(forms.ModelForm):
    class Meta:
        model = Semigroup
        fields = ('name', 'day', 'hour', 'room')

class WAForm(forms.ModelForm):
    class Meta:
        model = Workshop
        exclude = ('start_at', 'active_until', 'status')

    def __init__(self, data=None, **kwargs):
        super(WAForm, self).__init__(data=data, **kwargs)
        self.fields['semigroup'].queryset = Semigroup.objects.all().order_by('name')


@staff_required
def workshop_home(request, **kwargs):

    return render_to_response('workshop/cpanel/index.html',
                        {'module': 'workshop',
                         'days': DAY_CHOICES,
                         'semigroups': Semigroup.objects.all().order_by('name'),
                         'hours': range(8, 22, 2),
                         'info': WorkshopGame},
                        context_instance=RequestContext(request)
    )

@staff_required
def add_group(request):
    if request.method == 'POST':
        form = AGForm(request.POST)
        if form.is_valid():
            sg = form.save()
            sg.owner = WorkshopGame.get_instance()
            sg.save()
            return redirect('ws_edit_spot', day=sg.day, hour=sg.hour)
    else:
        form = AGForm()

    return render_to_response('workshop/cpanel/addgroup.html',
                        {'module': 'workshop',
                         'form': form,
                         },
                        context_instance=RequestContext(request)
    )

@staff_required
def edit_group(request, semigroup):
    semigroup = get_object_or_404(Semigroup, pk=semigroup)

    if request.method == 'POST':
        form = AGForm(request.POST, instance=semigroup)
        if form.is_valid():
            sg = form.save()
            sg.owner = WorkshopGame.get_instance()
            sg.save()
            return redirect('ws_edit_spot', day=sg.day, hour=sg.hour)
    else:
        form = AGForm(instance=semigroup)

    return render_to_response('workshop/cpanel/editgroup.html',
                        {'module': 'workshop',
                         'form': form,
                         'instance': semigroup,
                         },
                        context_instance=RequestContext(request)
    )


@staff_required
def edit_spot(request, day, hour):
    day, hour = int(day), int(hour)
    sgs = Semigroup.get_by_day_and_hour(day, hour)

    if not sgs:
        return redirect('ws_add_group')

    if request.method == 'POST':
        semigroup = get_object_or_404(Semigroup, pk=request.GET.get('semigroup'))
        try:
            player = Player.objects.get(pk=int(request.POST.get('player')))
        except (ValueError, Player.DoesNotExist):
            pass
        else:
            semigroup.add_player(player)

    return render_to_response('workshop/cpanel/editspot.html',
                        {'module': 'workshop',
                         'semigroups': sgs,
                         },
                        context_instance=RequestContext(request)
    )

@staff_required
def kick_off(request, player):
    player = get_object_or_404(Player, pk=player)

    sgs = player.playergroup_set.filter(owner=WorkshopGame.get_instance())
    for s in sgs:
        s.players.remove(player)

    return redirect('workshop_home')

@staff_required
def schedule(request):
    schedules = Schedule.objects.all().order_by('start_date', 'name')

    return render_to_response('workshop/cpanel/schedule.html',
                        {'module': 'workshop',
                         'schedules': schedules,
                         'category': WorkshopGame.get_question_category(),
                         'page': 'schedule'},
                        context_instance=RequestContext(request)
    )

@staff_required
def schedule_change(request, schedule=None):
    if schedule:
        schedule = get_object_or_404(Schedule, pk=schedule)

    if request.method == 'POST':
        form = SCForm(request.POST, instance=schedule)
        if form.is_valid():
            sc = form.save()
            sc.category = WorkshopGame.get_question_category()
            sc.save()
            return redirect('ws_schedule')
    else:
        form = SCForm(instance=schedule)

    return render_to_response('workshop/cpanel/schedule_change.html',
                        {'module': 'workshop',
                         'form': form,
                         'instance': schedule,
                         'page': 'schedule'},
                        context_instance=RequestContext(request)
    )


class WorkshopList(ListView):
    model = Workshop
    template_name = 'workshop/cpanel/workshops.html'
    paginate_by = 25
    context_object_name = 'workshops'

    def get_queryset(self):
        return self.model.objects.all().order_by('-active_until')

    def get_context_data(self, **kwargs):
        context = super(WorkshopList, self).get_context_data(**kwargs)
        context.update({'module': 'workshop', 'page': 'workshops', 'info': WorkshopGame,
                        'integrity_check': self.request.GET.get('integrity_check', False)
        })
        return context

workshops = staff_required(WorkshopList.as_view())

#@staff_required
#def workshops_old(request):
#    workshops = Workshop.objects.all().order_by('-active_until')
#    return render_to_response('workshop/cpanel/workshops.html',
#                        {'module': 'workshop',
#                         'workshops': workshops,
#                         'page': 'workshops',
#                         'info': WorkshopGame,
#                         'integrity_check': request.GET.get('integrity_check', False),
#                         },
#                        context_instance=RequestContext(request)
#    )

@staff_required
def workshop_mark4review(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)

    if workshop.is_started():
        WorkshopGame.start_reviewing(workshop)

    return redirect('ws_workshops')

@staff_required
def workshop_mark4grading(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)

    if workshop.is_reviewable():
        workshop.set_gradable()

    return redirect('ws_workshops')


@staff_required
def workshop_update_grades(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)

    for ass in workshop.assessment_set.all():
        ass.update_grade()

    return redirect('ws_reviewers_map', workshop=workshop.id)

@staff_required
def workshop_reviewers(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)

    if workshop.is_started():
        return redirect('ws_workshops')

    assessments = workshop.assessment_set.all().order_by('player__user__last_name', 'player__user__first_name')

    return render_to_response('workshop/cpanel/workshop_map.html',
                        {'module': 'workshop',
                         'workshop': workshop,
                         'assessments': assessments,
                         'page': 'workshops',
                         'integrity_check': request.GET.get('integrity_check', False),
                         },
                        context_instance=RequestContext(request)
    )


def get_next_assessment(assessment):
    """
    Find the next assessment in list (ordered alphabetically)
    """
    assessments = list(assessment.workshop.assessment_set.all().order_by('player__user__last_name', 'player__user__first_name'))
    index = assessments.index(assessment)
    if index == len(assessments) - 1:
        return None
    return assessments[index + 1]


@staff_required
def workshop_grade_assessment(request, assessment):
    assessment = get_object_or_404(Assessment, pk=assessment)
    assistant = request.user.get_profile()
    next_ass = get_next_assessment(assessment)

    if request.method == 'POST':
        data = request.POST
        for a in assessment.answer_set.all():
            try:
                grade = int(data.get('grade_%d' % a.id, ''))
            except ValueError:
                pass
            else:
                a.grade = grade
                a.save()

            # Update review
            feedback = data.get('feedback_%d' % a.id, '')
            review = Review.objects.get_or_create(answer=a, reviewer=assistant)[0]
            review.feedback = feedback
            review.save()

            # Update other reviews' grades
            for r in a.review_set.all():
                try:
                    grade = int(data.get('review_grade_%d' % r.id, ''))
                except ValueError:
                    pass
                else:
                    r.review_grade = grade
                    r.review_reviewer = assistant
                    r.save()
        # Grade the entire assessment
        assessment.update_grade()
        submit = data.get('submit', 'save')
        if submit == 'save':
            pass
        elif submit == 'save_return':
            return redirect('ws_reviewers_map', workshop=assessment.workshop.id)
        elif submit == 'save_next':
            if next_ass:
                return redirect('ws_grade_assessment', assessment=next_ass.id)
            else:
                return redirect('ws_reviewers_map', workshop=assessment.workshop.id)

    return render_to_response('workshop/cpanel/workshop_grade_assessment.html',
                        {'module': 'workshop',
                         'assessment': assessment,
                         'next_ass': next_ass,
                         'page': 'workshops',
                         },
                         context_instance=RequestContext(request)
    )


@staff_required
def workshop_add(request):
    error = ''
    if request.method == 'POST':
        form = WAForm(request.POST)
        if form.is_valid():
            error = WorkshopGame.create_workshop(semigroup=form.cleaned_data['semigroup'],
                                    date=form.cleaned_data['date'],
                                    question_count=form.cleaned_data['question_count']
            )
            if not error:
                return redirect('ws_workshops')
    else:
        form = WAForm()

    return render_to_response('workshop/cpanel/workshop_add.html',
                        {'module': 'workshop', 'form': form, 'info': WorkshopGame, 'error': error,
                         'page': 'workshops'},
                        context_instance=RequestContext(request)
    )


@staff_required
def workshop_edit(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)

    class WForm(forms.ModelForm):
        class Meta:
            model = Workshop
            exclude = ('status',)

    if request.method == 'POST':
        form = WForm(request.POST, instance=workshop)
        if form.is_valid():
            form.save()
            return redirect('ws_workshops')
    else:
        form = WForm(instance=workshop)

    return render_to_response('workshop/cpanel/workshop_edit.html',
                        {'module': 'workshop', 'form': form, 'info': WorkshopGame,
                         'page': 'workshops'},
                        context_instance=RequestContext(request)
    )


@staff_required
def workshop_start(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)
    workshop.start() # set start_at and active_until
    return redirect('ws_workshops')


@staff_required
def workshop_stop(request, workshop):
    workshop = get_object_or_404(Workshop, pk=workshop)
    workshop.stop() # set active_until
    return redirect('ws_workshops')


@staff_required
def workshop_assessments(request, workshop, assessment=None):
    workshop = get_object_or_404(Workshop, pk=workshop)
    if assessment:
        assessment = get_object_or_404(Assessment, pk=assessment)

    return render_to_response('workshop/cpanel/workshop_assessments.html',
                        {'module': 'workshop', 'page': 'workshops', 'workshop': workshop, 'assessment': assessment},
                        context_instance=RequestContext(request)
    )


@staff_required
def workshop_assessment_edit(request, assessment, **kwargs):
    assessment = get_object_or_404(Assessment, pk=assessment)

    for q in assessment.questions.all():
        Answer.objects.get_or_create(question=q, assessment=assessment)

    if request.method == 'POST':
        for a in assessment.answer_set.all():
            text = request.POST.get('answer_%d' % a.id, '')
            if text:
                a.text = text
                a.save()
    return render_to_response('workshop/cpanel/workshop_assessment_change.html',
                              {'module': 'workshop', 'page': 'workshops', 'workshop': assessment.workshop, 'assessment': assessment},
                              context_instance=RequestContext(request)
    )


@staff_required
def reset_reviews(request, workshop, assessment):
    """
    Remove all non expected reviews given to this assessment
    """
    assessment = get_object_or_404(Assessment, pk=assessment)
    for a in assessment.answer_set.all():
        for r in a.review_set.all():
            if r.reviewer not in list(assessment.reviewers.all()) and not r.reviewer.in_staff_group():
                r.delete()

    return redirect('ws_reviewers_map', workshop=assessment.workshop.id)


@staff_required
def gradebook(request, semigroup):
    """
    List all students and grades
    """
    semigroup = get_object_or_404(Semigroup, pk=semigroup)
    players = semigroup.players.all().order_by('user__last_name', 'user__first_name')

    return render_to_response('workshop/cpanel/gradebook.html',
                        {'module': 'workshop', 'page': 'workshops', 'semigroup': semigroup, 'players': players},
                        context_instance=RequestContext(request)
    )
