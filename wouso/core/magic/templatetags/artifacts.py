import django
from wouso.core.magic.models import Spell, PlayerArtifactAmount, PlayerSpellAmount, PlayerSpellDue


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
    group = unicode(artifact.group).lower()

    if isinstance(artifact, Spell):
        type = artifact.get_type_display()
    else:
        type = ''

    if path[0] == '/':
        html = '<img class="artifact" src="%s" alt="%s" title="%s" />' % (path, title, title)
    else:
        html = '<div class="artifact artifact-%s artifact-%s artifact-%s" title="%s"></div>' % (group, type, path, title)

    if amount is not None and amount > 1:
        return '<span class="artifact-container">%s<span class="sup">%d</span></span>' % (html, amount)
    else:
        return html


@register.simple_tag
def artifact_full(artif):
    if not artif:
        return ''
    return artifact(artif) + artif.title


@register.simple_tag
def spell_due(psd):
    html = artifact(psd)

    return '<span class="artifact-container" title="%s until %s">%s<span class="sup">*</span></span>' % \
                (psd.spell.title, psd.due, html)


@register.simple_tag
def spell_unknown(spell=None):
    return '<span class="artifact artifact-unknown" title="Unknown"></span>'
