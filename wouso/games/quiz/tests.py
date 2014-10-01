import json
import unittest

from datetime import datetime,timedelta
from mock import patch
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client, RequestFactory
from django.utils.translation import ugettext as _

from wouso.core.qpool.models import Question, Answer, Category
from wouso.core.tests import WousoTest
from wouso.games.quiz.models import Quiz, QuizUser, QuizGame

class QuizTestCase(WousoTest):
    def setUp(self):
        super(QuizTestCase, self).setUp()

    def tearDown(self):
        pass

    def _get_foo_question(self, correct=2):
        """ Return a Question """
        class Question: pass
        class Answer: pass
        q = Question()
        q.text = 'How many'
        q.answers = []
        for i in range(4):
            a = Answer()
            a.id, a.text, a.correct = i, str(i), True if i == correct else False
            q.answers.append(a)
        return q

    def testQuizCreate(self):
        q = Quiz.create(False)
