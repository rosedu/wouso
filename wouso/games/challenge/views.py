from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from wouso.core.config.models import Setting, BoolSetting
from wouso.core.user.models import Player
from wouso.games.challenge.models import ChallengeException
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
        return do_result(request, error='Your race can\'t play. Go home')

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
        form.check_self_boxes()
        if results.get('results', False):
            results['results'] = form.get_results_in_order(results['results'])
            questions_and_answers = zip(form.visible_fields(), results['results'])
        else:
            questions_and_answers = None
        return render_to_response('challenge/result.html',
            {'challenge': chall, 'challenge_user': chall_user, 'points': results['points'], 'form' : form,  'questions_and_answers' : questions_and_answers},
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
        return do_result(request, error=_('Sorry, challenge failed.'))

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
        #Checking if user_to is stored in session
        PREFIX = "_user:"
        action_msg = "multiple-login"
        if (PREFIX + user_to.user.username) in request.session:
            from wouso.core.signals import addActivity
            addActivity.send(sender=None, user_to=user_to, user_from=user_from, action=action_msg,
                             game=None, public=False)
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
    if not request.user.is_authenticated():
        return ''
    chall_user = request.user.get_profile().get_extension(ChallengeUser)
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
    setting = BoolSetting.get('disable-challenge-random').get_value()
    if setting:
        messages.error(request, _('Random challenge disabled'))
        return redirect('challenge_index_view')
    current_player = request.user.get_profile().get_extension(ChallengeUser)

    # selects challengeable players
    players = ChallengeUser.objects.exclude(user = current_player.user)
    players = players.exclude(race__can_play=False)
    players = [p for p in players if current_player.can_challenge(p)]

    if not players:
        messages.error(request, _('There is no one you can challenge now.'))
        return redirect('challenge_index_view')

    no_players = len(players)

    # selects the user to be challenged
    import random
    i = random.randrange(0, no_players)

    return launch(request, players[i].id)

@login_required
def detailed_challenge_stats(request, target_id, player_id=None):
    """ Statistics for one pair of users, current_player and target_id """
    if player_id and request.user.get_profile().in_staff_group():
        current_player = get_object_or_404(Player, pk=player_id).get_extension(ChallengeUser)
    else:
        current_player = request.user.get_profile().get_extension(ChallengeUser)

    target_user = get_object_or_404(ChallengeUser, user__id=target_id)

    from django.db.models import Q

    chall_total = Challenge.objects.filter(Q(user_from__user = current_player) |
            Q(user_to__user = current_player)).exclude(status=u'L')

    chall_total = chall_total.filter(Q(user_from__user=target_user) |
            Q(user_to__user=target_user)).order_by('-date')

    return render_to_response('challenge/statistics_detail.html',
            {'current_player' : current_player, 'target_player' : target_user,
                'chall_total' : chall_total,
                'opponent' : target_user},
            context_instance=RequestContext(request))

@login_required
def challenge_stats(request, player_id=None):
    """ Statistics for one user """
    if player_id and request.user.get_profile().in_staff_group():
        current_player = get_object_or_404(Player, pk=player_id).get_extension(ChallengeUser)
    else:
        current_player = request.user.get_profile().get_extension(ChallengeUser)

    from django.db.models import Avg, Q

    chall_total = Challenge.objects.filter(Q(user_from__user=current_player) |
            Q(user_to__user=current_player)).exclude(status=u'L')
    chall_sent = chall_total.filter(user_from__user=current_player)
    chall_rec = chall_total.filter(user_to__user=current_player)
    chall_won = chall_total.filter(winner=current_player)

    n_chall_sent = chall_sent.count()
    n_chall_rec = chall_rec.count()
    n_chall_played = chall_sent.count() + chall_rec.count()
    n_chall_won = chall_won.count()
    n_chall_ref = chall_total.filter(status=u'R').count()
    all_participation = Participant.objects.filter(user = current_player)

    opponents_from = list(set(map(lambda x : x.user_to.user, chall_sent)))
    opponents_to = list(set(map(lambda x : x.user_from.user, chall_rec)))
    opponents = list(set(opponents_from + opponents_to))

    result = []

    for op in opponents:
        chall_against_op = chall_total.filter(Q(user_to__user=op) |
                Q(user_from__user=op))
        won = chall_against_op.filter(Q(status=u'P') & Q(winner=current_player)).count()
        lost = chall_against_op.filter(Q(status=u'P') & Q(winner=op)).count()
        draw = chall_against_op.filter(Q(status=u'D')).count()
        refused = chall_against_op.filter(Q(status=u'R')).count()
        total = won + lost + draw + refused
        result.append((op, won, lost, draw, refused, total))

    result.sort(key=lambda by:by[5], reverse=True) #sort by total

    average_time = all_participation.aggregate(Avg('seconds_took'))['seconds_took__avg']
    average_score = all_participation.aggregate(Avg('score'))['score__avg']

    if average_time == None : average_time = 0
    if average_score == None : average_score = 0

    win_percentage = 0
    if n_chall_played > 0:
        win_percentage = float(n_chall_won) / n_chall_played * 100

    #pretty print the float for the template
    win_percentage = '%.1f' % win_percentage

    return render_to_response('challenge/statistics.html',
        {'n_chall_played' : n_chall_played, 'n_chall_won' : n_chall_won,
            'n_chall_sent' : n_chall_sent, 'n_chall_rec' : n_chall_rec,
            'n_chall_ref' : n_chall_ref, 'win_percentage' : win_percentage,
            'average_time' : average_time, 'average_score' : average_score,
            'current_player' : current_player, 'opponents' : result
            },
        context_instance=RequestContext(request))
