from django import template

register = template.Library()

@register.simple_tag
def artifact(artifact):
    if artifact.path[0] == '/':
        return '<img class="artifact" src="%s" />' % artifact.path
    
    return '<div class="artifact artifact-%s"></div>' % artifact.path
