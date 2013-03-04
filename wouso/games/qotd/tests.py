import json
import logging
import django.test
from django.contrib.auth.models import User
from models import *
from wouso.core.tests import WousoTest
from wouso.core.user.models import Player
from wouso.core import scoring
from wouso.core.qpool.models import Question, Schedule, Tag, Category


class QotdTestCase(WousoTest):
    def setUp(self):
        super(QotdTestCase, self).setUp()
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)
        scoring.setup_scoring()

    def _get_foo_question(self, correct=2):
        """ Return a Question object selected for Today """
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

    def testUserCreate(self):
        user,new = User.objects.get_or_create(username='_test2')

        profile = user.get_profile()

        self.assertTrue(isinstance(profile, Player))
        self.assertTrue(isinstance(profile.get_extension(QotdUser), QotdUser))

        user.delete()

    def testAnswered(self):
        correct = 2
        q = self._get_foo_question(correct)

        h1 = scoring.history_for(self.user, QotdGame)

        QotdGame.answered(self.qotd_user, q, correct - 1)
        # Check if history didn't change
        self.assertEqual(len(h1), len(scoring.history_for(self.qotd_user, QotdGame)))

        # Answer correctly
        self.qotd_user.reset_answered()

        QotdGame.answered(self.qotd_user, q, correct)
        # History changed
        h2 = scoring.history_for(self.qotd_user, QotdGame)
        self.assertGreater(len(h2), len(h1))

        coins = scoring.user_coins(self.qotd_user)
        self.assertGreater(coins['points'], 0)

    def test_multiple_qotd(self):
        """ Test if game selects any of multiple qotd provided
        """
        q1 = _make_question_for_today(self.user, 'test1')
        q2 = _make_question_for_today(self.user, 'test2')

        for i in range(4):
            a = QotdGame.get_for_today()
            self.assertTrue(a in (q1, q2))

def _make_question_for_today(user, text):
    category = Category(name='qotd')
    question = Question(text=text, proposed_by=user, category=category, active=1)
    question.save()
    for i in range(4):
        Answer.objects.create(question=question, correct=i==1, text='a %d'%i)
    sched = Schedule(question=question)
    sched.save()
    return question

class PageTests(WousoTest):
    def setUp(self):
        super(PageTests, self).setUp()
        self.user = User.objects.create(username='_test')
        self.user.set_password('_test_pw')
        self.user.save()
        profile = self.user.get_profile()
        self.qotd_user = profile.get_extension(QotdUser)
        scoring.setup_scoring()
        self.client.login(username='_test', password='_test_pw')

    def testNoQuestion(self):
        response = self.client.get('/g/qotd/')
        self.assertContains(response, 'No question for today.')

    def testCorrectAnswer(self):
        _make_question_for_today(user=self.user, text="what is the question?")
        response = self.client.get('/g/qotd/')
        self.assertContains(response, 'No question for today.', 0)
        self.assertContains(response, 'what is the question?')

    def test_question_response_and_done(self):
        _make_question_for_today(user=self.user, text="what is the question?")
        response = self.client.get('/g/qotd/')
        self.assertContains(response, 'what is the question')
        response_form = self.client.post('/g/qotd/', {'answers': 2}, follow=True)
        self.assertContains(response_form, '[correct]')


class ApiTest(WousoTest):

    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.set_password('pw')
        self.user.save()
        super(ApiTest, self).setUp()

    def test_answer_qotd(self):
        q = _make_question_for_today(user=self.user, text="api question")
        qotduser = self.user.get_profile().get_extension(QotdUser)
        qotduser.reset_answered()

        self.client.login(username='_test', password='pw')
        response = self.client.get('/api/qotd/today/')

        data = json.loads(response.content)
        self.assertTrue(data)

        correct = q.correct_answers[0]

        # Attempt response
        response = self.client.post('/api/qotd/today/', {'answer': correct.id})
        data = json.loads(response.content)

        self.assertTrue(data['success'])
        self.assertTrue(data['correct'])

        # Assert has_answered
        self.assertTrue(data['has_answered'])
        # force reload
        qotduser = QotdUser.objects.get(pk=qotduser.pk)
        self.assertTrue(qotduser.has_answered)

        # Check another answer
        wrong = q.answers[3]

        response = self.client.post('/api/qotd/today/', {'answer': wrong.id})
        data = json.loads(response.content)

        self.assertFalse(data['success']) # because already answered
        self.assertEqual(data['error'], 'User already answered')
        qotduser.reset_answered()

        response = self.client.post('/api/qotd/today/', {'answer': wrong.id})
        data = json.loads(response.content)

        self.assertTrue(data['success'])
        self.assertFalse(data['correct'])
