import django
from wouso.core.user.models import (PlayerArtifactAmount,
                                    PlayerSpellAmount,
                                    PlayerSpellDue)

register = django.template.Library()

@register.simple_tag
def artifact(artifact):
    if not artifact:
        return '(no artifact)'

    if isinstance(artifact, PlayerArtifactAmount):
        amount = artifact.amount
        artifact = artifact.artifact
    elif isinstance(artifact, PlayerSpellAmount):
        amount = artifact.amount
        artifact = artifact.spell
    elif isinstance(artifact, PlayerSpellDue):
        amount = None
        artifact = artifact.spell
    else:
        amount = None
    path = artifact.path
    title = artifact.title

    if path[0] == '/':
        html = '<img class="artifact" src="%s" alt="%s" title="%s" />' % (path, title, title)
    else:
        html = '<div class="artifact artifact-%s" title="%s"></div>' % (path, title)

    if amount is not None:
        return '<span class="artifact-container">%s<span class="sup">%d</span></span>' % (html, amount)
    else:
        return html

@register.simple_tag
def artifact_full(artif):
    if not artif:
        return ''
    return artifact(artif) + artif.title

@register.simple_tag
def spell_due(spell):
    html = artifact(spell.spell)

    return '<span class="artifact-container" title="%s until %s">%s<span class="sup">*</span>' % \
                (spell.spell.title, spell.due, html)

@register.simple_tag
def spell_unknown(spell=None):
    return '<div class="artifact artifact-unknown" title="Unknown"></div>'
