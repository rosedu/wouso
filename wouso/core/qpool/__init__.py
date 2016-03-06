# TODO: check usage of these functions and rename/refactor
from django.db import models
from django.db.models import Q
from wouso.core.qpool.models import Question


def get_questions_with_tags(tlist, select='any', active_only=True, endorsed_only=True):
    if isinstance(tlist, str):
        result = Question.objects.filter(tags__name=tlist)
    else:
        if select == 'any':
            tfilters = Q(tags__name=tlist[0])
            for t in tlist[1:]:
                tfilters = tfilters | Q(tags__name=t)
            result = Question.objects.filter(tfilters)
        elif select == 'all':
            result = Question.objects.filter(tags__name=tlist[0])
            for t in tlist[1:]:
                result = result.filter(tags__name=t)
    # more filtering
    if active_only:
        result = result.filter(active=True)
    if endorsed_only:
        result = result.exclude(endorsed_by__isnull=True)
    return result


def get_questions_with_category(category='all', active_only=True, endorsed_only=False):
    ''' can be called with all, string for category name or instance of Category '''
    if category == 'all':
        result = Question.objects.all()
    elif isinstance(category, str):
        result = Question.objects.filter(category__name=category)
    elif isinstance(category, models.Category):
        result = Question.objects.filter(category=category)

    # filtering
    if active_only:
        result = result.filter(active=True)
    if endorsed_only:
        result = result.exclude(endorsed_by__isnull=True)

    return result


def get_questions_with_tag_and_category(tag=None, category='all', active_only=True, endorsed_only=False):
    result = Question.objects.filter(tags__name=tag, category__name=category).distinct()

    # filtering
    if active_only:
        result = result.filter(active=True)
    if endorsed_only:
        result = result.exclude(endorsed_by__isnull=True)

    return result


def get_questions_with_tag_for_day(tag, select):
    if isinstance(tag, str):
        query = Question.objects.filter(tags__name=tag).exclude(endorsed_by__isnull=True)
        for q in query:
            if q.day == select:
                return q
        return None


# Public API
def register_category(category_name, game=None):
    """
     Register a new category so questions in this category can be added and filtered.
    """
    # TODO: use it everywhere
    from . import models
    try:
        return models.Category.objects.get_or_create(name=category_name)[0]
    except:
        return None
