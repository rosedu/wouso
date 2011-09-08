import django

register = django.template.Library()

@register.simple_tag
def artifact(artifact):
    path = artifact.path if artifact else ' '
    title = artifact.title if artifact else '(no title)'
    if path[0] == '/':
        return '<img class="artifact" src="%s" alt="%s" title="%s" />' % (path, title, title)

    return '<div class="artifact artifact-%s" title="%s"></div>' % (path, title)

@register.simple_tag
def artifact_full(artif):
    if not artif:
        return ''
    return artifact(artif) + artif.title
