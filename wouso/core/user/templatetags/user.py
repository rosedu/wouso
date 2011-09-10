from md5 import md5
from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.artifacts.templatetags.artifacts import artifact
register = template.Library()

@register.simple_tag
def player(user):
    if isinstance(user, str):
        return ''

    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    artif_html = artifact(user.level)
    return u'<a href="%s">%s%s</a>' % (link, artif_html, user)

@register.simple_tag
def player_simple(user):
    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    return u'<a href="%s">%s</a>' % (link, user)

@register.simple_tag
def player_simple2(user, user2):
    link = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    if user == user2:
        name = _('You')
    else:
        name = unicode(user)

    return u'<a href="%s">%s</a>' % (link, name)

@register.simple_tag
def player_group(group):
    link = reverse('wouso.interface.profile.views.player_group', args=(group.id,))

    return u'<a href="%s">%s</a>' % (link, group)

@register.simple_tag
def player_avatar(player_obj):
    avatar = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid" % md5(player_obj.user.email).hexdigest()

    return avatar
