from md5 import md5
from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.user.models import Player
from wouso.core.scoring.models import Coin
from wouso.core.magic.templatetags.artifacts import artifact
register = template.Library()

@register.simple_tag
def player(user):
    """ Render player name and level image with link to player's profile """
    if isinstance(user, str):
        return ''

    if isinstance(user, int) or isinstance(user, long):
        user = Player.objects.get(pk=user)

    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    artif_html = artifact(user.level)
    return u'<a href="%s">%s%s</a>' % (link, artif_html, user)

@register.simple_tag
def player_simple(user):
    """ Render only the player name with link to player's profile """
    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    if hasattr(user, 'level'):
        return u'<a href="%s" title="%s [%d]">%s</a>' % (link, user.level.title if user.level else '', user.level_no, user)
    else:
        return u'<a href="%s" >%s</a>' % (link, user)

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
    avatar = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid" % md5(player_obj.user.email).hexdigest()

    return avatar

@register.simple_tag
def coin_amount(amount, coin=None):
    if coin is None:
        coin = Coin.get('points')
    else:
        coin = Coin.get(coin)

    if coin is None:
        return '%f (not setup)' % amount

    return '<div class="coin-amount coin-%s" title="%s">%s</div>' % (coin.name, coin.name, amount)

@register.simple_tag
def spell_stock(player, spell):
    if player is None:
        return ''
    stock = player.spell_stock(spell)
    return 'x%d' % stock if stock > 0 else '-'

@register.simple_tag
def player_input(name):

    return '<input type="hidden" name="{name}" id="ac_input_{name}_value" />' \
           '<input type="text" id="ac_input_{name}" class="ac_input big" />' \
           '<script>setAutocomplete("#ac_input_{name}");</script>'.format(name=name)