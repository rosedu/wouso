from django import template
from wouso.games.workshop.models import Semigroup

register = template.Library()

@register.simple_tag
def get_schedule(day, hour):
    """ Render player name and level image with link to player's profile """

    return Semigroup.get_by_day_and_hour(day, hour)