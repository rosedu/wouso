from django import template
from hashlib import md5
from django.core.urlresolvers import reverse

register = template.Library()

def user(profile, format):
    format = format.split()
    return {'gravatar_link': "http://www.gravatar.com/avatar/" + md5(profile.user.email).hexdigest() + ".jpg?d=monsterid",
            'user_profile_link': reverse('user_profile', kwargs={'id': profile.user.id}),
            'user_full_name': profile.user.get_full_name(),
            'format': format}

register.inclusion_tag('user/profile_tags.html')(user)