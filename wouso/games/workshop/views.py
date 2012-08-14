from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from models import WorkshopGame
from wouso.games.workshop.models import Assesment, Workshop

@login_required
def index(request, extra_context=None):
    player = request.user.get_profile()
    assesment = Assesment.get_for_player_and_workshop(request.user.get_profile(), WorkshopGame.get_for_now())

    if not extra_context:
        extra_context = {}

    extra_context.update({'workshopgame': WorkshopGame, 'workshop': WorkshopGame.get_for_player_now(player),
                          'assesment': assesment})

    return render_to_response('workshop/index.html',
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
    workshop = WorkshopGame.get_for_now()
    player = request.user.get_profile()
    error = ''

    if not workshop:
        return do_error(request, _('No current workshop'))
    elif player not in workshop.semigroup.players.all():
        return do_error(request, _('You are not in the current semigroup'))

    assesment = Assesment.objects.get_or_create(player=player, workshop=workshop)[0]
    if assesment.answered:
        return do_error(request, _('You have already answered this workshop'))

    if request.method == 'POST':
        answers = {}
        for q in workshop.questions.all():
            answers[q.id] = request.POST.get('answer_%d' % q.id)

        assesment.set_answered(answers)
        return redirect('workshop_index_view')

    return render_to_response('workshop/play.html',
                {'assesment': assesment,
                 'workshop': workshop},
                context_instance=RequestContext(request)
    )

@login_required
def review(request, workshop):
    player = request.user.get_profile()
    workshop = get_object_or_404(Workshop, pk=workshop)

    assesment = Assesment.get_for_player_and_workshop(player, workshop)

    if not assesment:
        return do_error(_('Cannot review an workshop you did not participate to.'))

    assesments = player.assesments_review.filter(workshop=workshop)

    return render_to_response('workshop/review.html',
                {'assesment': assesment,
                 'workshop': workshop,
                 'assesments': assesments},
                context_instance=RequestContext(request)
    )