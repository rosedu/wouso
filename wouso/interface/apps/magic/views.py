from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_noop
from exceptions import ValueError
from wouso.core.config.models import BoolSetting
from wouso.core.scoring.sm import InvalidFormula
from wouso.core.user.models import Player
from wouso.core.magic.models import Spell, SpellHistory, PlayerSpellDue, Artifact, Bazaar
from wouso.core import scoring, signals
from wouso.interface.activity.models import Activity

# marche
def bazaar(request, message='', error=''):
    player = request.user.get_profile() if request.user.is_authenticated() else None
    spells = Spell.objects.all().order_by('-available', 'level_required')

    # Disable exchange for real
    exchange_disabled = BoolSetting.get('disable-Bazaar-Exchange').get_value()
    try:
        rate = scoring.calculate('gold-points-rate', gold=1)['points']
        rate2 = round(1/scoring.calculate('points-gold-rate', points=1)['gold'])
    except InvalidFormula:
        rate, rate2 = 1, 1
    rate_text = _('Rate: 1 gold = {rate} points, 1 gold = {rate2} points').format(rate=rate, rate2=rate2)

    cast_spells = PlayerSpellDue.objects.filter(source=player).all()
    unseen_count = cast_spells.filter(seen=False).count()

    # TODO: think of smth better
    cast_spells.update(seen=True)

    # get all significant magic activity
    activity_list = Activity.objects.filter(Q(action='spell-buy') | Q(action='earned-ach') | Q(action__contains='gold') | Q(action='cast')).order_by('-timestamp')

    paginator = Paginator(activity_list, 40)
    try:
        activity = paginator.page(1)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

    return render_to_response('magic/bazaar.html', {'spells': spells,
                              'activity': activity,
                              'rate': rate, 'rate_text': rate_text,
                              'cast': cast_spells,
                              'unseen_count': unseen_count,
                              'theowner': player,
                              'message': message,
                              'exchange_disabled': exchange_disabled,
                              'error': error},
                              context_instance=RequestContext(request))

@login_required
def bazaar_exchange(request):
    gold_rate = scoring.calculate('gold-points-rate', gold=1)['points']
    points_rate = scoring.calculate('points-gold-rate', points=1)['gold']

    player = request.user.get_profile()
    message, error = '', ''
    if BoolSetting.get('disable-Bazaar-Exchange').get_value():
        error = _("Exchange is disabled")
    elif request.method == 'POST':
        try:
            points = float(request.POST.get('points', 0))
            gold = round(float(request.POST.get('gold', 0)))
        except:
            error = _('Invalid amounts')
        else:
            if points != 0:
                gold = points_rate * points
                if gold > 0:
                    if player.points < points:
                        error = _('Insufficient points')
                    else:
                        points = round(gold) / points_rate
                        scoring.score(player, None, 'points-gold-rate', points=points)
                        message = _('Converted successfully')
                else:
                    error = _('Insufficient points')
            # other way around
            elif gold != 0:
                points = gold_rate * gold
                if player.coins['gold'] < gold:
                    error = _('Insufficient gold')
                else:
                    scoring.score(player, None, 'gold-points-rate', gold=gold)
                    message = _('Converted successfully')
            else:
                error = _('Unknown action')
    else:
        error = _('Expected post')

    return render_to_response('magic/bazaar_buy.html',
                {'error': error,
                'message': message, 'tab': 'exchange'},
                context_instance=RequestContext(request))

@login_required
def bazaar_buy(request, spell):
    spell = get_object_or_404(Spell, pk=spell)

    player = request.user.get_profile()
    error, message = '',''

    if Bazaar.disabled():
        error = _("Magic is disabled")
    elif spell.price > player.coins.get('gold', 0):
        error = _("Insufficient gold amount")
    elif spell.available == False:
        error = _("Spell is not available")
    elif spell.level_required > player.level_no:
        error = _("Level {level} is required to buy this spell").format(level=spell.level_required)
    else:
        player.magic.add_spell(spell)
        scoring.score(player, None, 'buy-spell', external_id=spell.id,
                      price=spell.price)
        signal_msg = ugettext_noop('bought a spell')
        action_msg = 'spell-buy'
        signals.addActivity.send(sender=None, user_from=player,
                        user_to=player,
                        message=signal_msg,
                        game=None,
                        action=action_msg,
                        public=False)
        SpellHistory.bought(player, spell)
        message = _("Successfully aquired")

    return bazaar(request, message=message, error=error)


@login_required
def magic_cast(request, destination=None, spell=None):
    player = request.user.get_profile()
    destination = get_object_or_404(Player, pk=destination)

    error = ''

    if Bazaar.disabled():
        error = _("Magic is disabled")
    elif request.method == 'POST':
        spell = get_object_or_404(Spell, pk=request.POST.get('spell', 0))
        try:
            days = int(request.POST.get('days', 0))
        except ValueError:
            pass
        else:
            if (days > spell.due_days) or ((spell.due_days > 0) and (days < 1)):
                error = _('Invalid number of days')
            else:
                due = datetime.now() + timedelta(days=days)
                if not spell.mass:
                    error = destination.magic.cast_spell(spell=spell, source=player, due=due)
                else:
                    players = destination.get_neighbours_from_top(2, player.race, spell.type)
                    players = player.magic.filter_players_by_spell(players, spell)
                    error = player.magic.mass_cast(spell=spell, destination=players, due=due)

                if not error:
                    return HttpResponseRedirect(reverse('wouso.interface.profile.views.user_profile', args=(destination.id,)))

                error = _('Cast failed:') + ' ' + error

    return render_to_response('profile/cast.html',
                              {'destination': destination, 'error': error},
                              context_instance=RequestContext(request))


@login_required
def affected_players(request):
    try:
        spell_id = int(request.GET.get('spell_id', None))
        user_id = int(request.GET.get('user', None))
    except:
        raise Http404
    spell = get_object_or_404(Spell, pk=spell_id)

    if spell.mass:
        user = request.user.get_profile()
        destination = get_object_or_404(Player, pk=user_id)
        players = destination.get_neighbours_from_top(2, user.race, spell.type)
        players = user.magic.filter_players_by_spell(players, spell)
    else :
        user = get_object_or_404(Player, pk=user_id)
        players = [user]

    return render_to_response('profile/mass_cast_players_list.html', { 'players':players }, context_instance=RequestContext(request))


@login_required
def artifact_hof(request, artifact=None):
    """
     Hall of Fame for Artifacts (generaly achievements)
    """
    artifact = get_object_or_404(Artifact, pk=artifact) if artifact else None

    artifacts = Artifact.objects.all().annotate(used=Count('playerartifactamount')).filter(group__name='Default').order_by('-used')
    players = Player.objects.all().annotate(owned=Count('playerartifactamount')).exclude(owned=0).order_by('-owned')[:10]

    return render_to_response('magic/artifact_hof.html', {'artifacts': artifacts, 'players': players, 'artifact': artifact},
        context_instance=RequestContext(request))
