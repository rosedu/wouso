from django.db.models import Q

def get_questions_with_tags(tlist, select='any'):
    if isinstance(tlist, str):
        return models.Question.objects.filter(tags__name=tlist).exclude(endorsed_by__isnull=True)
    else:
        if select == 'any':
            tfilters = Q(tags__name=tlist[0])
            for t in tlist[1:]:
                tfilters = tfilters | Q(tags__name=t)
            return models.Question.objects.filter(tfilters).exclude(endorsed_by__isnull=True)
        elif select == 'all':
            result = models.Question.objects.filter(tags__name=tlist[0]).exclude(endorsed_by__isnull=True)
            for t in tlist[1:]:
                result = result.filter(tags__name=t)
            return result

def get_questions_with_tag_for_day(tag, select):
    if isinstance(tag, str):
        query = models.Question.objects.filter(tags__name=tag).exclude(endorsed_by__isnull=True)
        for q in query:
            if q.day == select:
                return q
        return None
