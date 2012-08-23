from django import template
from django.db.models import Sum
from wouso.games.workshop.models import Semigroup, Review

register = template.Library()

@register.simple_tag
def get_schedule(day, hour):
    """ Render player name and level image with link to player's profile """

    return Semigroup.get_by_day_and_hour(day, hour)

@register.simple_tag
def get_reviewer_grade(workshop, player):
    """ Render sum of grades from reviewer
    """
    qs = Review.objects.filter(answer__assesment__workshop=workshop, reviewer=player)
    if not qs.count():
        return None
    else:
        return qs.aggregate(grade=Sum('answer_grade'))['grade']

@register.simple_tag
def get_answer_feedback(answer, player):
    """ Render the feedback text, if  a review by player was given to answer
    """

    qs = Review.objects.filter(answer=answer, reviewer=player)
    if not qs.count():
        return ''
    return qs.get().feedback