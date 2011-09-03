from datetime import datetime
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
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

    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return do_error(request, 'inexistent')

    if not chall_user.can_play(chall):
        return do_error(request, 'cantplay')

    if request.method == 'GET' and not chall.is_started_for_user(request.user.get_profile()):
        chall.set_start(request.user.get_profile())

    if request.method == "POST":
        # check time delta between start of challenge and submit
        if not chall.check_timedelta(request.user.get_profile()):
            return do_error(request, 'Challenge timer exceeded.')

        form = ChallengeForm(chall, request.POST)

        results = chall.set_played(chall_user, form.get_response())

        return render_to_response('challenge/result.html',
            {'challenge': chall, 'results': results},
            context_instance=RequestContext(request))
    else:
        form = ChallengeForm(chall)
    return render_to_response('challenge/challenge.html',
            {'challenge': chall, 'form': form},
            context_instance=RequestContext(request))


@login_required
def launch(request, to_id):
    try:
        user_to = User.objects.get(id=to_id)
        user_to = user_to.get_profile().get_extension(ChallengeUser)
    except User.DoesNotExist:
        return do_error(request, 'nosuchuser')

    user_from = request.user.get_profile().get_extension(ChallengeUser)

    if user_from.can_challenge(user_to):

        chall = Challenge.create(user_from=user_from, user_to=user_to)
        if not chall:
            """ Some error occurred during question fetch. Clean up, and display error """
            return do_error(request, 'couldnotcreate')


        return HttpResponseRedirect(reverse('games.challenge.views.index'))
    else:
        return do_error(request, 'cannotchallenge')



@login_required
def accept(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return do_error(request, 'nosuchchallenge')

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_to.user == user_to and chall.is_launched():
        chall.accept()
        return HttpResponseRedirect(reverse('games.challenge.views.index'))
    else:
        print chall.user_to, user_to, chall.is_launched()
    return do_error(request, 'cannotaccept')

@login_required
def refuse(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return do_error(request, 'nosuchchallenge')

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_to.user == user_to and chall.is_launched():
        chall.refuse()
        return HttpResponseRedirect(reverse('games.challenge.views.index'))
    return do_error(request, 'cannotrefuse')

@login_required
def cancel(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return do_error(request, 'nosuchchallenge')

    user_from = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_from.user == user_from and chall.is_launched():
        chall.cancel()
        return HttpResponseRedirect(reverse('games.challenge.views.index'))
    return do_error(request, 'cannotcancel')

def header_link(request):
    profile = request.user.get_profile()
    if not profile:
        return ''
    chall_user = profile.get_extension(ChallengeUser)
    challs = ChallengeGame.get_active(chall_user)
    challs = [c for c in challs if not (c.status == 'L' and c.user_from.user == chall_user)]
    count = len(challs)

    link = '<a href="'+ reverse('games.challenge.views.index') +'">' + _('Challenges') + '</a>'

    if count > 0:
        link += '<span class="unread-count">%d</span>' % count
    return link
