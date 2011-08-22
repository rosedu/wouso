from django import template

register = template.Library()

@register.simple_tag
def artifact(artifact):
    path = artifact.path if artifact else ' '
    if path[0] == '/':
        return '<img class="artifact" src="%s" />' % path

    return '<div class="artifact artifact-%s"></div>' % path

@register.simple_tag
def artifact_full(artif):
    if not artif:
        return ''
    return artifact(artif) + artif.title
