from django import template
from django.core.urlresolvers import reverse
from wouso.core.artifacts.templatetags.artifacts import artifact
register = template.Library()

@register.simple_tag
def player(user):
    if isinstance(user, str):
        return ''
    artif_html = artifact(user.level)
    user_profile = reverse('wouso.interface.profile.views.user_profile', args=(user.id,))

    return u'<a href="%s">%s%s</a>' % (user_profile, artif_html, user)

@register.simple_tag
def player_group(group):
    link = reverse('wouso.interface.profile.views.player_group', args=(group.id,))

    return u'<a href="%s">%s</a>' % (link, group)
