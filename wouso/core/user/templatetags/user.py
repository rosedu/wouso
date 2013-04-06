from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.decorators import cached_method
from wouso.core.user.models import Player
from wouso.core.scoring.models import Coin
from wouso.core.magic.templatetags.artifacts import artifact
register = template.Library()

@register.simple_tag
def player(user, artif_html=None, real_name=False):
    """ Render player name and level image with link to player's profile """
    if not user or isinstance(user, str):
        return ''

    if isinstance(user, int) or isinstance(user, long):
        user = Player.objects.get(pk=user)

    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    if artif_html is None:
        artif_html = artifact(user.level)

    rel_data = u"%s,%s,%s,%s,%s,%s,1" % (user.nickname, user.full_name, user.points, player_avatar(user), user.level_no, user.id)
    if user.in_staff_group():
        staff_class = 'cplayer-staff'
    else:
        staff_class = 'cplayer-%s' % user.race_name.lower()
    if real_name:
        name = u'%s %s (%s)' % (user.user.first_name, user.user.last_name, user.user.username)
    else:
        name = u'%s' % user
    return u'<a href="%s" class="cplayer %s" rel="%s">%s%s</a>' % (link, staff_class, rel_data, artif_html, name)


@register.simple_tag
def player_simple(user, real_name=False):
    """ Render only the player name with link to player's profile """
    return player(user, artif_html='', real_name=real_name)


@register.simple_tag
def player_simple2(user, user2):
    """ Render name as You if player is the same as to user argument """
    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    if user == user2:
        name = _('You')
    else:
        name = unicode(user)

    return u'<a href="%s">%s</a>' % (link, name)

@register.simple_tag
def player_group(group):
    """ Render group with link to group's profile page """
    if group:
        link = reverse('wouso.interface.profile.views.player_group', args=(group.id,))

        return u'<a href="%s%s" title="%s">%s</a>' % (link, group, group.name, group)
    else:
        return ''

@register.simple_tag
def player_race(race):
    """ Render group with link to group's profile page """
    link = reverse('race_view', args=(race.id,))

    return u'<a href="%s%s" title="%s" class="cplayer-%s">%s</a>' % (link, race, race.name, race.name.lower(), race)


@register.simple_tag
def player_avatar(player_obj):
    """ Return avatar's URL using the gravatar service """
    if not isinstance(player_obj, Player):
        player_obj = Player.objects.get(pk=player_obj)
    return player_obj.avatar if player_obj else ''


@register.simple_tag
def coin_amount(amount, coin=None):
    if coin is None:
        coin = Coin.get('points')
    else:
        coin = Coin.get(coin)

    if coin is None:
        return '(not setup)'

    if amount is None:
        return '(none)'

    if isinstance(amount, Player):
        amount = amount.coins.get(coin.name, 0)

    amount = coin.format_value(amount)

    return '<div class="coin-amount coin-%s" title="%s">%s</div>' % (coin.name, coin.name, amount)

@register.simple_tag
def spell_stock(player, spell):
    if player is None:
        return ''
    stock = player.magic.spell_stock(spell)
    return 'x%d' % stock if stock > 0 else '-'

@register.simple_tag
def player_input(name, id=None):
    id = id if id else name

    func_content = '{' + 'setAutocomplete("#ac_input_{id}");'.format(id=id) + '}'
    return '<input type="hidden" placeholder="Player..." name="{name}" id="ac_input_{id}_value" />\n' \
           '<input type="text" id="ac_input_{id}" class="ac_input big" />\n' \
           '<script>$(document).ready(function() {func_content});</script>'.format(name=name, id=id, func_content=func_content)
