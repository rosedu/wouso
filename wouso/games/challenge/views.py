from datetime import datetime
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from wouso.core.user.models import Player
from wouso.games.challenge.models import ChallengeException
from wouso.interface import render_string
from models import ChallengeUser, ChallengeGame, Challenge, Participant
from forms import ChallengeForm

@login_required
def index(request):
    """ Shows all challenges related to the current user """
    profile = request.user.get_profile()
    chall_user = profile.get_extension(ChallengeUser)

    challs = ChallengeGame.get_active(chall_user)
    played = ChallengeGame.get_played(chall_user)[:10]

    if not chall_user.is_eligible():
        return do_result(request, error='Ne pare rau, nu esti anul I, nu poti provoca. Te invitam pe wouso-next.rosedu.org')

    return render_to_response('challenge/index.html',
            {'challenges': challs, 'played': played, 'challuser': chall_user, 'challenge': ChallengeGame},
            context_instance=RequestContext(request))

@login_required
def do_result(request, error='', message=''):
    return render_to_response('challenge/message.html',
        {'error': error, 'message': message},
        context_instance=RequestContext(request))

@login_required
def challenge(request, id):
    """ Displays a challenge, only if status = accepted
    This is play """
    chall_user = request.user.get_profile().get_extension(ChallengeUser)

    chall = get_object_or_404(Challenge, pk=id)

    # check to see if challenge was already submitted
    try:
        participant = chall.participant_for_player(chall_user)
    except:
        raise Http404

    if participant.played:
        return do_result(request, _('You have already submitted this challenge'\
                                   ' and scored %.2f points') % participant.score)

    # this is caught by chall_user
    #if not chall_user.can_play(chall):
    #    return do_result(request, _('You cannot play this challenge.'))

    if request.method == 'GET' and not chall.is_started_for_user(chall_user):
        chall.set_start(chall_user)

    if request.method == "POST":
        form = ChallengeForm(chall, request.POST)

        results = chall.set_played(chall_user, form.get_response())

        return render_to_response('challenge/result.html',
            {'challenge': chall, 'results': results},
            context_instance=RequestContext(request))
    else:
        form = ChallengeForm(chall)

    seconds_left = chall.time_for_user(chall_user)
    return render_to_response('challenge/challenge.html',
            {'challenge': chall, 'form': form, 'challenge_user': chall_user, 'seconds_left': seconds_left},
            context_instance=RequestContext(request))


@login_required
def launch(request, to_id):
    user_to = get_object_or_404(Player, pk=to_id)

    user_to = user_to.get_extension(ChallengeUser)

    user_from = request.user.get_profile().get_extension(ChallengeUser)

    if ChallengeGame.disabled():
        return do_result(request, error='Provocarile sunt dezactivate')

    if (not user_to.is_eligible()) or (not user_from.is_eligible()):
        return do_result(request, error='Ne pare rau, doar studentii de anul I pot provoca/fi provocati')

    if not user_from.can_launch():
        return do_result(request, _('You cannot launch another challenge today.'))

    if not user_from.has_enough_points():
        return do_result(request, _('You need at least 30 points to launch a challenge'))

    if user_from.can_challenge(user_to):
        try:
            chall = Challenge.create(user_from=user_from, user_to=user_to)
        except ChallengeException as e:
            # Some error occurred during question fetch. Clean up, and display error
            return do_result(request, e.message)
        return do_result(request, message=_('Successfully challenged'))
    else:
        return do_result(request, _('This user cannot be challenged.'))


@login_required
def accept(request, id):
    if ChallengeGame.disabled():
        return do_result(request, error='Provocarile sunt dezactivate')

    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.accept()
            return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_result(request, _('Challenge cannot be accepted.'))

@login_required
def refuse(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.refuse()
            return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_result(request, _('You cannot refuse this challenge.'))

@login_required
def cancel(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_from = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_from.user == user_from and chall.is_launched():
        chall.cancel()
        return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_result(request, _('You cannot cancel this challenge.'))

@login_required
def setplayed(request, id):
    """ Set challenge as played for the other user.
    Only superuser can do this. Useful for debugging
    """
    if not request.user.is_superuser:
        raise Http404

    chall = get_object_or_404(Challenge, pk=id)

    if chall.user_from.played:
        chall.user_to.played = True
        chall.user_to.score = 0
    else:
        chall.user_from.played = True
        chall.user_from.score = 0

    chall.played()
    return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))

@login_required
def use_one_more(request):
    challuser = request.user.get_profile().get_extension(ChallengeUser)

    if challuser.has_one_more():
        challuser.do_one_more()
    else:
        return do_result(_("You don't have the artifact."))
    return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))

def header_link(request):
    profile = request.user.get_profile()
    if profile:
        chall_user = profile.get_extension(ChallengeUser)
        challs = ChallengeGame.get_active(chall_user)
        # remove launched challenges by the user
        challs = [c for c in challs if not (c.status == 'L' and c.user_from.user == chall_user)]
        # remove refused challenges
        challs = [c for c in challs if not c.status == 'R']

        count = len(challs)
    else:
        count = 0
    url = reverse('wouso.games.challenge.views.index')

    return dict(link=url, count=count, text=_('Challenges'))

def sidebar_widget(request):
    profile = request.user.get_profile()
    if not profile:
        return ''
    chall_user = profile.get_extension(ChallengeUser)
    challs = ChallengeGame.get_active(chall_user)
    challs = [c for c in challs if c.status == 'A']
    # reduce noise, thanks
    if not challs:
        return ''

    return render_to_string('challenge/sidebar.html', {'challenges': challs, 'challenge': ChallengeGame,  'chall_user': chall_user})

def history(request, playerid):
    player = get_object_or_404(ChallengeUser, pk=playerid)

    challs = [p.challenge for p in Participant.objects.filter(user=player)]
    challs = sorted(challs, key=lambda c: c.date)

    return render_to_response('challenge/history.html', {'challplayer': player, 'challenges': challs},
                              context_instance=RequestContext(request))


def challenge_random(request):

    current_player = request.user.get_profile().get_extension(ChallengeUser)

    # selects challengeable players
    players = ChallengeUser.objects.exclude(user = current_player.user)
    players = players.exclude(race__can_play=False)
    players = [p for p in players if current_player.can_challenge(p)]

    no_players = len(players)

    # selects the user to be challenged
    import random
    i = random.randrange(0, no_players)

    return launch(request, players[i].id)

