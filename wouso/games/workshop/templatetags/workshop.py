# coding=utf-8
from django import template
from django.db.models import Sum
from wouso.games.workshop.models import Semigroup, Review

register = template.Library()

@register.simple_tag
def semigroup(sg):
    if not sg:
        return ''

    return u"<b>%s</b> [%d] %s" % (sg.name, sg.players.count(), sg.room)


@register.simple_tag
def get_schedule(day, hour):
   return ', '.join([semigroup(s) for s in Semigroup.get_by_day_and_hour(day, hour)])


@register.simple_tag
def get_reviewer_grade(workshop, player):
    """ Render sum of grades from reviewer
    """
    qs = Review.objects.filter(answer__assessment__workshop=workshop, reviewer=player)
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