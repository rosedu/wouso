# coding=utf-8
from django import template
from django.db.models import Sum
from wouso.games.workshop.models import Semigroup, Review, ROOM_DEFAULT

register = template.Library()

@register.simple_tag
def semigroup(sg):
    if not sg:
        return ''

    if sg.room == ROOM_DEFAULT:
        return u"<b>%s</b> <span class='points'>%d</span>" % (sg.name, sg.players.count())
    return u"<b>%s</b> %s <span class='points'>%d</span>" % (sg.name, sg.room, sg.players.count())


@register.simple_tag
def get_schedule(day, hour):
   return '<br/> '.join([semigroup(s) for s in Semigroup.get_by_day_and_hour(day, hour)])


@register.simple_tag
def get_ass_reviewer_grade(assessment, player):
    """ Render sum of grades from player reviewer, for a specific assessment
    So player reviewed assessment and gave it this results.
    """
    qs = Review.objects.filter(answer__assessment=assessment, reviewer=player)

    return qs.aggregate(grade=Sum('answer_grade'))['grade']


@register.simple_tag
def get_ass_review_grade(assessment, player):
    """ Render sum of review grades for a specific assessment and player

    So player reviewed assessment, and received from the assistant this grade.
    """
    qs = Review.objects.filter(answer__assessment=assessment, reviewer=player)

    return qs.aggregate(grade=Sum('review_grade'))['grade']


@register.simple_tag
def get_answer_feedback(answer, player):
    """ Render the feedback text, if  a review by player was given to answer
    """

    qs = Review.objects.filter(answer=answer, reviewer=player)
    if not qs.count():
        return ''
    return qs.get().feedback

@register.simple_tag
def get_final_grade(workshop, player):
    assessment = workshop.get_assessment(player)

    return assessment.final_grade if assessment else None
