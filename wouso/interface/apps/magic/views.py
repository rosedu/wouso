from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_noop
from django.views.generic import ListView
from exceptions import ValueError
from wouso.core.config.models import BoolSetting
from wouso.core.scoring.sm import InvalidFormula
from wouso.core.user.models import Player
from wouso.core.magic.models import Spell, SpellHistory, PlayerSpellDue, Artifact, Bazaar
from wouso.core import scoring, signals
from wouso.interface.activity.models import Activity

class BazaarView(ListView):
    template_name = 'magic/bazaar.html'
    context_object_name = 'activity'
    paginate_by = 40

    def get_queryset(self):
        activity_list = Activity.objects.filter(Q(action='spell-buy') | Q(action='earned-ach') | 
                            Q(action__contains='gold') | Q(action='cast')).order_by('-timestamp')
        return activity_list

    def get_context_data(self, **kwargs):
        context = super(BazaarView, self).get_context_data(**kwargs)
        player = self.request.user.get_profile() if self.request.user.is_authenticated() else None
        spells = Spell.objects.all().order_by('-available', 'level_required')

        cast_spells = PlayerSpellDue.objects.filter(source=player).all()
        unseen_count = cast_spells.filter(seen=False).count()

        # TODO: think of smth better
        cast_spells.update(seen=True)

        context.update({'spells': spells,
                        'cast': cast_spells,
                        'unseen_count': unseen_count,
                        'theowner': player})
        return context

bazaar = BazaarView.as_view()

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
        message = _("Successfully acquired")

    if error:
        messages.error(request, error)
    if message:
        messages.success(request, message)

    return redirect('bazaar_home')

@login_required
def magic_cast(request, destination=None, spell=None):
    player = request.user.get_profile()
    destination = get_object_or_404(Player, pk=destination)

    error = ''

    if Bazaar.disabled() or BoolSetting.get('disable-Magic').get_value():
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

    if error:
        messages.error(request, error)

    return render_to_response('profile/cast.html',
                              {'destination': destination},
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
