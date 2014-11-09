from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from wouso.core import scoring
from wouso.core.user.models import Player
from wouso.core.tests import WousoTest
from wouso.games.quiz.models import Quiz, QuizUser, QuizGame


class QuizTestCase(WousoTest):
    def setUp(self):
        super(QuizTestCase, self).setUp()
        self.user = User.objects.create(username='test')
        self.user.save()
        self.quiz_user = self.user.get_profile().get_extension(QuizUser)
        scoring.setup_scoring()
        QuizGame.get_instance().save()

    def tearDown(self):
        self.user.delete()

    def test_user_create(self):
        user, new = User.objects.get_or_create(username='test')
        profile = user.get_profile()
        self.assertTrue(isinstance(profile, Player))
        self.assertTrue(isinstance(profile.get_extension(QuizUser), QuizUser))


class TestQuizViews(WousoTest):
    def setUp(self):
        super(TestQuizViews, self).setUp()
        # create super user
        self.super_user = self._get_superuser()

        # create player with index 1
        self.quiz_user = self._get_player(1)
        self.quiz_user = self.quiz_user.get_extension(QuizUser)

        scoring.setup_scoring()

        # username must be 'testuser + index' as defined in WousoTest class
        self.c = Client()
        self.c.login(username='testuser1', password='test')

    def test_quiz_index_view(self):
        # check before adding any quiz
        response = self.c.get(reverse('quiz_index_view'))
        self.assertContains(response, 'No quizzes have been added yet. Stay tuned!')

        # create quiz
        Quiz.objects.create(name='TestingQuiz', start=datetime.now(), end=datetime.now())

        # check after adding a quiz
        response = self.c.get(reverse('quiz_index_view'))
        self.assertContains(response, 'TestingQuiz')
    
    def test_quiz_view(self):
        # Not working properly
        # TODO: figure out how to add question q in quiz
        q = _make_question(text='Are you there?')
        quiz = Quiz.objects.create(name='TestingQuiz', start=datetime.now(), end=datetime.now())
        response = self.c.get(reverse('quiz_view', kwargs={'id': quiz.id}))


def _make_question(text='How many', correct=2):
    class Question: pass
    class Answer: pass
    q = Question()
    q.text = text
    q.answers = []
    for i in range(4):
        a = Answer()
        a.id = i
        a.text = 'ans' + str(i)
        a.correct = True if i == correct else False
        q.answers.append(a)
    return q
