from datetime import datetime
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from wouso.core.user.models import Player
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

    return render_to_response('challenge/index.html',
            {'challenges': challs, 'played': played, 'challuser': chall_user},
            context_instance=RequestContext(request))

@login_required
def do_error(request, error=''):
    return render_to_response('challenge/error.html',
        {'error': error},
        context_instance=RequestContext(request))

@login_required
def challenge(request, id):
    """ Displays a challenge, only if status = accepted
    This is play """
    chall_user = request.user.get_profile().get_extension(ChallengeUser)

    chall = get_object_or_404(Challenge, pk=id)

    if not chall_user.can_play(chall):
        return do_error(request, 'cantplay')

    if request.method == 'GET' and not chall.is_started_for_user(request.user.get_profile()):
        chall.set_start(request.user.get_profile())

    # check time delta between start of challenge
    if not chall.check_timedelta(request.user.get_profile()):
        # set challenge lost for user
        chall.expired(request.user.get_profile())
        return do_error(request, 'Challenge timer exceeded.')

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
    try:
        user_to = Player.objects.get(id=to_id)
        user_to = user_to.get_extension(ChallengeUser)
    except User.DoesNotExist:
        return do_error(request, 'nosuchuser')

    user_from = request.user.get_profile().get_extension(ChallengeUser)

    if user_from.can_challenge(user_to):

        try:
            chall = Challenge.create(user_from=user_from, user_to=user_to)
        except ValueError as e:
            """ Some error occurred during question fetch. Clean up, and display error """
            return do_error(request, e.message)


        return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    else:
        return do_error(request, 'cannotchallenge')


@login_required
def accept(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.accept()
            return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_error(request, 'cannotaccept')

@login_required
def refuse(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.refuse()
            return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_error(request, 'cannotrefuse')

@login_required
def cancel(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_from = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_from.user == user_from and chall.is_launched():
        chall.cancel()
        return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))
    return do_error(request, 'cannotcancel')

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
    else:
        chall.user_from.played = True

    chall.played()
    return HttpResponseRedirect(reverse('wouso.games.challenge.views.index'))

def header_link(request):
    profile = request.user.get_profile()
    if not profile:
        return ''
    chall_user = profile.get_extension(ChallengeUser)
    challs = ChallengeGame.get_active(chall_user)
    # remove launched challenges by the user
    challs = [c for c in challs if not (c.status == 'L' and c.user_from.user == chall_user)]
    # remove refused challenges
    challs = [c for c in challs if not c.status == 'R']

    count = len(challs)

    link = '<a href="'+ reverse('wouso.games.challenge.views.index') +'">' + _('Challenges') + '</a>'

    if count > 0:
        link += '<span class="unread-count">%d</span>' % count
    return link

def sidebar_widget(request):
    profile = request.user.get_profile()
    if not profile:
        return ''
    chall_user = profile.get_extension(ChallengeUser)
    challs = ChallengeGame.get_active(chall_user)
    challs = [c for c in challs if c.status == 'A']

    return render_string('challenge/sidebar.html', {'challenges': challs, 'chall_user': chall_user})
