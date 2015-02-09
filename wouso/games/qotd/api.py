from django.db import models
from django.http import Http404
from piston.handler import BaseHandler
from models import QotdGame, QotdUser
from wouso.core.qpool.models import Answer


class QotdHandler(BaseHandler):
    methods_allowed = ('GET', 'POST')

    def read(self, request):
        question = QotdGame.get_for_today()
        try:
            qotduser = request.user.get_profile().get_extension(QotdUser)
        except models.Model.DoesNotExist:
            raise Http404()
        if question:
            return {'text': question, 'answers': dict([(a.id, a) for a in question.answers]),
                    'had_answered': qotduser.has_answered}
        return {}

    def create(self, request):
        question = QotdGame.get_for_today()
        try:
            qotduser = request.user.get_profile().get_extension(QotdUser)
        except models.Model.DoesNotExist:
            raise Http404()
        if not question:
            return {'success': False, 'error': 'No question for today'}
        if qotduser.has_answered:
            return {'success': False, 'error': 'User already answered'}
        attrs = self.flatten_dict(request.data)
        if 'answer' not in attrs.keys():
            return {'success': False, 'error': 'Answer not provided'}
        try:
            answer_id = int(attrs['answer'])
            answer = Answer.objects.get(pk=answer_id)
        except ValueError, Answer.DoesNotExist:
            return {'success': False, 'error': 'Invalid answer'}
        else:
            qotduser.set_answered(answer.id, answer.correct)
            return {'success': True, 'correct': answer.correct, 'has_answered': qotduser.has_answered}