from md5 import md5
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.user.models import Player
from wouso.core.scoring.models import Coin
from wouso.core.magic.templatetags.artifacts import artifact
register = template.Library()

@register.simple_tag
def player(user):
    """ Render player name and level image with link to player's profile """
    if not user or isinstance(user, str):
        return ''

    if isinstance(user, int) or isinstance(user, long):
        user = Player.objects.get(pk=user)

    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    artif_html = artifact(user.level)
    rel_data = u"%s,%s,%s,%s,%s,%s,1" % (user.nickname, user.user.first_name, user.points, player_avatar(user), user.level_no, user.id)
    return u'<a href="%s" class="cplayer" rel="%s">%s%s</a>' % (link, rel_data, artif_html, user)

@register.simple_tag
def player_simple(user):
    """ Render only the player name with link to player's profile """
    if not user:
        return ''

    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))
    rel_data_simple = u"%s,%s,%s,%s,%s,%s,1" % (user.nickname, user.user.first_name, user.points, player_avatar(user), user.level_no, user.id)

    if hasattr(user, 'level'):
        return u'<a href="%s" rel="%s" class="cplayer">%s</a>' % (link, rel_data_simple, user)
    else:
        return u'<a href="%s" rel="%s" class="cplayer">%s</a>' % (link, rel_data_simple, user)

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

    return u'<a href="%s%s" title="%s">%s</a>' % (link, race, race.name, race)

@register.simple_tag
def player_avatar(player_obj):
    """ Return avatar's URL using the gravatar service """
    if not player_obj:
        return ''

    avatar = "http://www.gravatar.com/avatar/%s.jpg?d=%s" % (md5(player_obj.user.email).hexdigest(), settings.AVATAR_DEFAULT)

    return avatar

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
    stock = player.spell_stock(spell)
    return 'x%d' % stock if stock > 0 else '-'

@register.simple_tag
def player_input(name, id=None):
    id = id if id else name

    return '<input type="hidden" name="{name}" id="ac_input_{id}_value" />' \
           '<input type="text" id="ac_input_{id}" class="ac_input big" />' \
           '<script>setAutocomplete("#ac_input_{id}");</script>'.format(name=name, id=id)
