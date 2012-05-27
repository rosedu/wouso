from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.config.models import BoolSetting
from wouso.core.user.models import Player, PlayerSpellDue
from wouso.core.magic.models import Spell, SpellHistory
from wouso.core import scoring

# marche
def bazaar(request, message='', error=''):
    player = request.user.get_profile() if request.user.is_authenticated() else None
    spells = Spell.objects.all()

    rate = scoring.calculate('gold-points-rate', gold=1)['points']
    rate2 = round(1/scoring.calculate('points-gold-rate', points=1)['gold'])
    rate_text = _('Rate: 1 gold = {rate} points, 1 gold = {rate2} points').format(rate=rate, rate2=rate2)

    cast_spells = PlayerSpellDue.objects.filter(source=player).all()
    unseen_count = cast_spells.filter(seen=False).count()

    # TODO: think of smth better
    cast_spells.update(seen=True)
    return render_to_response('magic/bazaar.html', {'spells': spells,
                              'rate': rate, 'rate_text': rate_text,
                              'cast': cast_spells,
                              'unseen_count': unseen_count,
                              'theowner': player,
                              'message': message,
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
    if spell.price > player.coins.get('gold', 0):
        error = _("Insufficient gold amount")
    else:
        player.add_spell(spell)
        scoring.score(player, None, 'buy-spell', external_id=spell.id,
                      price=spell.price)
        SpellHistory.bought(player, spell)
        message = _("Successfully aquired")

    return bazaar(request, message=message, error=error)
    # TODO: use django-flash
    """
    return render_to_response('bazaar_buy.html',
                              {'error': error, 'message': message,
                              },
                              context_instance=RequestContext(request))
    """