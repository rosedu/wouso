from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic import View, ListView, TemplateView
from django.conf import settings
from wouso.core.config.models import Setting, BoolSetting
from wouso.core.ui import register_sidebar_block, register_header_link
from wouso.core.user.models import Player
from wouso.core.decorators import staff_required
from wouso.games.challenge.models import ChallengeException
from models import ChallengeUser, ChallengeGame, Challenge, Participant
from forms import ChallengeForm
import os
import fcntl
import logging
from django.db import transaction

@transaction.commit_manually
def flush_transaction():
    """ Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    transaction.commit()

class PlayerViewMixin():
    def get_player(self):
        if 'player_id' in self.kwargs.keys() and self.request.user.get_profile().in_staff_group():
            current_player = get_object_or_404(Player, pk=self.kwargs['player_id'])
            current_player = current_player.get_extension(ChallengeUser)
        else:
            current_player = self.request.user.get_profile().get_extension(ChallengeUser)

        return current_player

@login_required
def index(request):
    """ Shows all challenges related to the current user """
    profile = request.user.get_profile()
    chall_user = profile.get_extension(ChallengeUser)

    challs = ChallengeGame.get_active(chall_user)
    played = ChallengeGame.get_played(chall_user)[:10]

    if not chall_user.is_eligible():
        messages.error(request, _('Your race can\'t play. Go home'))

    return render_to_response('challenge/index.html',
            {'challenges': challs, 'played': played, 'challuser': chall_user, 'challenge': ChallengeGame},
            context_instance=RequestContext(request))

class ChallengeView(View):
    def dispatch(self, request, *args, **kwargs):
        self.chall_user = request.user.get_profile().get_extension(ChallengeUser)
        self.chall = get_object_or_404(Challenge, pk=kwargs['id'])
        try:
            self.participant = self.chall.participant_for_player(self.chall_user)
        except:
            raise Http404

        # Check if the player has accepted the challenge before playing it
        if self.chall.status == 'L':
            messages.error(request, _('The challenge was not accepted yet!'))
            return redirect('challenge_index_view')

        # Check if the self.challenge was refused
        if self.chall.status == 'R':
            messages.error(request, _('The challenge was refused!'))
            return redirect('challenge_index_view')

        if self.participant.played:
            messages.error(request, _('You have already submitted this challenge'\
                                       ' and scored %.2f points') % self.participant.score)
            return redirect('challenge_index_view')

        return super(ChallengeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.chall.is_started_for_user(self.chall_user):
            self.chall.set_start(self.chall_user)
        form = ChallengeForm(self.chall)
        seconds_left = self.chall.time_for_user(self.chall_user)
        return render_to_response('challenge/challenge.html',
                {'challenge': self.chall, 'form': form, 'challenge_user': self.chall_user,
                'seconds_left': seconds_left},
                context_instance=RequestContext(request))

    def post(self, request, **kwargs):
        form = ChallengeForm(self.chall, request.POST)
        results = self.chall.set_played(self.chall_user, form.get_response())
        form.check_self_boxes()

        if results.get('results', False):
            results['results'] = form.get_results_in_order(results['results'])
            questions_and_answers = zip(form.visible_fields(), results['results'])
        else:
            questions_and_answers = None
        return render_to_response('challenge/result.html',
            {'challenge': self.chall, 'challenge_user': self.chall_user,
            'points': results['points'], 'form' : form,  'questions_and_answers' : questions_and_answers},
            context_instance=RequestContext(request))

challenge = login_required(ChallengeView.as_view())

class FileLock:
    def __init__(self, filename):
        handle = open(filename, 'w')
        self.handle = handle
        fcntl.flock(handle, fcntl.LOCK_EX)

    def unlock(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None

    def __del__(self):
        if self.handle != None:
            self.unlock()

class NamedFileLock:
    def __init__(self, filename):
        self.filename = filename

    def lock(self):
        return FileLock(self.filename)

challengeLock = NamedFileLock("/tmp/wouso_challenge_launch_lock")

#import logging
#logger = logging.

# http://stackoverflow.com/questions/3346124/how-do-i-force-django-to-ignore-any-caches-and-reload-data

@login_required
def launch(request, to_id):
    lock = challengeLock.lock()
    logging.info("Locked.")

    flush_transaction()
    user_to = get_object_or_404(Player, pk=to_id)
    user_to = user_to.get_extension(ChallengeUser)
    user_from = request.user.get_profile().get_extension(ChallengeUser)


    if ChallengeGame.disabled():
        messages.error(request, _('Challenges have been disabled.'))
        logging.info("Ready to unlock (disabled).")
        lock.unlock()
        return redirect('challenge_index_view')

    if (not user_to.is_eligible()) or (not user_from.is_eligible()):
        messages.error(request, _('Sorry, challenge failed.'))
        logging.info("Ready to unlock (is eligible).")
        lock.unlock()
        return redirect('challenge_index_view')

    if not user_from.can_launch():
        messages.error(request, _('You cannot launch another challenge today.'))
        logging.info("Ready to unlock (cannot launch today).")
        lock.unlock()
        return redirect('challenge_index_view')

    if not user_from.in_same_division(user_to):
        messages.error(request, _('You are not in the same division'))
        logging.info("Ready to unlock (not in same divission).")
        lock.unlock()
        return redirect('challenge_index_view')

    if not user_from.has_enough_points():
        messages.error(request, _('You need at least 30 points to launch a challenge'))
        logging.info("Ready to unlock (not enough points).")
        lock.unlock()
        return redirect('challenge_index_view')

    if user_from.can_challenge(user_to):
        try:
            chall = Challenge.create(user_from=user_from, user_to=user_to)
            logging.info("Created challenge: %s" %(chall))
        except ChallengeException as e:
            # Some error occurred during question fetch. Clean up, and display error
            messages.error(request, e.message)
            lock.unlock()
            return redirect('challenge_index_view')
        #Checking if user_to is stored in session
        PREFIX = "_user:"
        action_msg = "multiple-login"
        if (PREFIX + user_to.user.username) in request.session:
            from wouso.core.signals import addActivity
            addActivity.send(sender=None, user_to=user_to, user_from=user_from, action=action_msg,
                             game=None, public=False)
        messages.success(request, _('Successfully challenged'))
        logging.info("Ready to unlock (save).")
        lock.unlock()
        return redirect('challenge_index_view')
    else:
        messages.error(request, _('This user cannot be challenged.'))
        logging.info("Ready to unlock (no user challenge).")
        lock.unlock()
        return redirect('challenge_index_view')

@login_required
def accept(request, id):
    if ChallengeGame.disabled():
        messages.error(request, _('Challenges are disabled'))
        return redirect('challenge_index_view')

    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.accept()
            return redirect('challenge_index_view')

    messages.error(request, _('Challenge cannot be accepted.'))
    return redirect('challenge_index_view')

@login_required
def refuse(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_to = request.user.get_profile().get_extension(ChallengeUser)
    if (chall.user_to.user == user_to and chall.is_launched()) or \
        request.user.is_superuser:
            chall.refuse()
            return redirect('challenge_index_view')

    messages.error(request, _('You cannot refuse this challenge.'))
    return redirect('challenge_index_view')

@login_required
def cancel(request, id):
    chall = get_object_or_404(Challenge, pk=id)

    user_from = request.user.get_profile().get_extension(ChallengeUser)
    if chall.user_from.user == user_from and chall.is_launched():
        chall.cancel()
        return redirect('challenge_index_view')

    messages.error(request, _('You cannot cancel this challenge.'))
    return redirect('challenge_index_view')

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
    return redirect('challenge_index_view')

@login_required
def use_one_more(request):
    challuser = request.user.get_profile().get_extension(ChallengeUser)

    if challuser.has_one_more():
        challuser.do_one_more()
    else:
        messages.error(request, _('You don\'t have the artifact'))

    return redirect('challenge_index_view')

def header_link(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return dict(text=_('Challenges'))

    if ChallengeGame.disabled():
        return ''

    profile = user.get_profile()
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
register_header_link('challenges', header_link)


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    chall_user = user.get_profile().get_extension(ChallengeUser)
    challs = ChallengeGame.get_active(chall_user)
    challs = [c for c in challs if c.status == 'A']
    # reduce noise, thanks
    if not challs:
        return ''
    return render_to_string('challenge/sidebar.html', {'challenges': challs,
                            'challenge': ChallengeGame,  'chall_user': chall_user, 'id': 'challenge'})
register_sidebar_block('challenge', sidebar_widget)


class HistoryView(ListView):
    template_name = 'challenge/history.html'
    context_object_name = 'challenges'

    def get_queryset(self):
        self.player = get_object_or_404(ChallengeUser, pk=self.kwargs['playerid'])
        challenges = [p.challenge for p in Participant.objects.filter(user=self.player)]
        challenges = sorted(challenges, key=lambda c: c.date)
        return challenges

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context.update({'challplayer': self.player})
        return context

history = HistoryView.as_view()

@login_required
def challenge_player(request):
    if request.method == 'POST':
        try:
            player_to_challenge = Player.objects.get(pk=int(request.POST.get('player')))
            player_to_challenge = player_to_challenge.get_extension(ChallengeUser)
            return launch(request, player_to_challenge.id)
        except (ValueError, Player.DoesNotExist):
            messages.error(request, _('Player does not exist'))
            return redirect('challenge_index_view')
    return redirect('challenge_index_view')

@login_required
def challenge_random(request):
    setting = BoolSetting.get('random_challenge').get_value()
    if setting:
        messages.error(request, _('Random challenge disabled'))
        return redirect('challenge_index_view')

    current_player = request.user.get_profile().get_extension(ChallengeUser)
    player = current_player.get_random_opponent()

    if not player:
        messages.error(request, _('There is no one you can challenge now.'))
        return redirect('challenge_index_view')

    return redirect('challenge_launch', player.id)

class DetailedChallengeStatsView(ListView, PlayerViewMixin):
    template_name = 'challenge/statistics_detail.html'
    context_object_name = 'chall_total'

    def get_queryset(self):
        self.target_user = get_object_or_404(ChallengeUser, id=self.kwargs['target_id'])
        return self.get_player().get_related_challenges(self.target_user)

    def get_context_data(self, **kwargs):
        context = super(DetailedChallengeStatsView, self).get_context_data(**kwargs)
        context.update({'current_player': self.get_player(),
                       'target_player': self.target_user,
                       'opponent': self.target_user})
        return context

detailed_challenge_stats = login_required(DetailedChallengeStatsView.as_view())

class ChallengeStatsView(TemplateView, PlayerViewMixin):
    """ Statistics for one user """
    template_name = 'challenge/statistics.html'

    def get_context_data(self, **kwargs):
        context = super(ChallengeStatsView, self).get_context_data(**kwargs)
        context.update(self.get_player().get_stats())
        return context

challenge_stats = login_required(ChallengeStatsView.as_view())
