from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from models import WorkshopGame, Semigroup, Workshop, Review


@login_required
def index(request, extra_context=None):
    player = request.user.get_profile()
    workshop = WorkshopGame.get_for_player_now(player)
    assessment = workshop.get_or_create_assessment(player) if workshop else None

    if not extra_context:
        extra_context = {}

    extra_context.update({'workshopgame': WorkshopGame, 'workshop': WorkshopGame.get_for_player_now(player),
                          'assessment': assessment, 'semigroup': Semigroup.get_by_player(player),
                          'history': player.assessments.all().order_by('-workshop__active_until')})

    return render_to_response(
        'workshop/index.html',
        extra_context,
        context_instance=RequestContext(request)
    )


def do_error(request, error):
    return index(request, extra_context={'error': error})


@login_required
def play(request):
    """
     Play current workshop or show expired message.
    """
    player = request.user.get_profile()
    workshop = WorkshopGame.get_for_player_now(player=player)

    if not workshop:
        return do_error(request, _('No workshop for you'))

    if not workshop.is_active():
        return do_error(request, _('Workshop is not active'))

    assessment = workshop.get_or_create_assessment(player=player)
    if assessment.answered:
        return do_error(request, _('You have already answered this workshop'))

    if request.method == 'POST':
        answers = {}
        for q in assessment.questions.all():
            answers[q.id] = request.POST.get('answer_%d' % q.id)

        assessment.set_answered(answers)
        return redirect('workshop_results', workshop=workshop.id)

    seconds_left = assessment.time_left()

    return render_to_response(
        'workshop/play.html',
        {'assessment': assessment,
         'workshop': workshop,
         'seconds_left': seconds_left},
        context_instance=RequestContext(request)
    )


@login_required
def review(request, workshop):
    player = request.user.get_profile()
    workshop = get_object_or_404(Workshop, pk=workshop)

    assessment = workshop.get_assessment(player)

    if not assessment:
        return do_error(request, _('Cannot review an workshop you did not participate to.'))

    assessments = player.assessments_review.filter(workshop=workshop)

    if request.method == 'POST':
        for ass in assessments:
            for answer in ass.answer_set.all():
                feedback = request.POST.get('feedback_%d' % answer.id, None)
                answer_grade = request.POST.get('grade_%d' % answer.id, None)

                if feedback is not None or answer_grade is not None:
                    review = Review.objects.get_or_create(reviewer=player, answer=answer)[0]
                    review.feedback = feedback
                    review.answer_grade = answer_grade
                    review.save()

    return render_to_response(
        'workshop/review.html',
        {'assessment': assessment,
         'workshop': workshop,
         'assessments': assessments},
        context_instance=RequestContext(request)
    )


@login_required
def review_change(request, review):
    review = get_object_or_404(Review, pk=review)
    player = request.user.get_profile()

    if review.reviewer != player:
        return do_error(request, _('Cannot change another review'))

    if not review.workshop.is_reviewable():
        return do_error(request, _('Workshop not reviewable'))

    class RCForm(forms.ModelForm):
        class Meta:
            model = Review
            fields = ('feedback', 'answer_grade')

    if request.method == 'POST':
        form = RCForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('workshop_review', workshop=review.workshop.id)
    else:
        form = RCForm(instance=review)

    return render_to_response(
        'workshop/review_change.html',
        {'review': review,
         'form': form},
        context_instance=RequestContext(request)
    )


@login_required
def results(request, workshop):
    player = request.user.get_profile()
    workshop = get_object_or_404(Workshop, pk=workshop)

    assessment = workshop.get_assessment(player)

    if not assessment:
        return do_error(request, _('Cannot view results for an workshop you did not participate to.'))

    return render_to_response(
        'workshop/results.html',
        {'assessment': assessment,
         'workshop': workshop},
        context_instance=RequestContext(request)
    )
