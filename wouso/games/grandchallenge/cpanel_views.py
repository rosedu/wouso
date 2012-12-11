from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from wouso.core.decorators import staff_required
from wouso.games.grandchallenge.models import GrandChallenge, GrandChallengeGame, Round


@staff_required
def grandchalls(request):
    round = GrandChallengeGame.get_current_round()
    nr = round.round_number if round else -1
    return render_to_response('grandchallenge/cpanel/grandchallenge.html',
        {'nr': nr, 'round': round, 'gc': GrandChallengeGame},
        context_instance=RequestContext(request))


@staff_required
def grandchalls_round_next(request):
    if request.method == 'POST':
        GrandChallengeGame.round_next()
        return redirect('grandchalls')
    return render_to_response('grandchallenge/cpanel/grandchallenge_round_next.html', {'gc': GrandChallengeGame},
                              context_instance=RequestContext(request))


@staff_required
def grandchalls_round_close(request):
    if request.method == 'POST':
        round = GrandChallengeGame.get_current_round()
        GrandChallengeGame.force_round_close(round)
        return redirect('grandchalls')
    return render_to_response('grandchallenge/cpanel/grandchallenge_round_close.html', {'gc': GrandChallengeGame},
                              context_instance=RequestContext(request))


@staff_required
def grandchalls_hard_reset(request):
    if request.method == 'POST':
        GrandChallengeGame.reset()
        return redirect('grandchalls')
    return render_to_response('grandchallenge/cpanel/grandchallenge_hard_reset.html', {'gc': GrandChallengeGame},
                              context_instance=RequestContext(request))


@staff_required
def grandchalls_round_results(request, round_number):
    round = Round(round_number)
    return render_to_response('grandchallenge/cpanel/grandchallenge_round_results.html', {'round': round, 'gc': GrandChallengeGame},
                              context_instance=RequestContext(request))


@staff_required
def grandchalls_results(request):
    return render_to_response('grandchallenge/cpanel/grandchallenge_results.html',
            {'gchalls': GrandChallenge.get_challenges(),
             'clasament': GrandChallenge.clasament()},
        context_instance=RequestContext(request))


@staff_required
def grandchalls_round(request):
    """ Play a round """
    # TODO: move logic to models.
    """ regular round """
    over = 0
    done = GrandChallenge.all_done()
    if not GrandChallengeGame.is_final():
        if done:
            GrandChallenge.joaca(GrandChallengeGame.round_number)
            if GrandChallengeGame.round_number % 2 == 0:
                GrandChallenge.play_round(1)
                GrandChallenge.play_round(0)
            else:
                GrandChallenge.play_round(1)
            GrandChallengeGame.round_number += 1
    else:
        """ final 2 players
            they may have to play 2 rounds if the winners finalist lose
            to the loosers finalist
        """
        if GrandChallengeGame.round_number != 10:
            GrandChallengeGame.final_round()
            GrandChallenge.joaca(GrandChallengeGame.round_number)
            GrandChallenge.play_round(1)
            GrandChallenge.play_round(0)
            if GrandChallengeGame.is_winner():
                over = 1
        else:
            if not GrandChallengeGame.is_winner():
                GrandChallengeGame.final_second_round()
            over = 1

        GrandChallengeGame.round_number += 1
    gchalls = sorted(GrandChallenge.get_challenges(), key=lambda gc:gc.branch)

    return render_to_response('grandchallenge/cpanel/grandchallenge.html',
            {'gchalls': gchalls,
             'nr': GrandChallengeGame.round_number,
             'done': done,
             'over': over},
        context_instance=RequestContext(request))


@staff_required
def grandchalls_start(request):
    """ Play the game """
    GrandChallengeGame.start()
    return redirect('grandchalls')

@staff_required
def grandchalls_set_active(request):
    """ Start the game """
    #GrandChallengeGame.set_active()
    return render_to_response('grandchallenge/cpanel/grandchallenge.html',
        context_instance=RequestContext(request))


@staff_required
def lastchalls(request):
    last30 = GrandChallenge.objects.filter(challenge__status__in=['P', 'D']).order_by('-challenge__date')[:30]
    return render_to_response('grandchallenge/cpanel/lastchalls.html',
            {'last30': last30},
        context_instance=RequestContext(request))