from django.db.models import Q

def get_questions_with_tags(tlist, select='any'):
    if isinstance(tlist, str):
        return models.Question.objects.filter(tags__name=tlist)
    else:
        if select == 'any':
            tfilters = Q(tags__name=tlist[0])
            for t in tlist[1:]:
                tfilters = tfilters | Q(tags__name=t)
            return models.Question.objects.filter(tfilters)
        elif select == 'all':
            result = models.Question.objects.filter(tags__name=tlist[0])
            for t in tlist[1:]:
                result = result.filter(tags__name=t)
            return result
