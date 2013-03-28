import json
import unittest
from datetime import datetime,timedelta
from mock import patch

from django.contrib.auth.models import User
from wouso.core.qpool.models import Question, Answer, Category
from wouso.core.tests import WousoTest
from wouso.games.challenge.models import ChallengeUser, Challenge, ChallengeGame
from wouso.core.user.models import Player
from wouso.core import scoring
from wouso.core.scoring.models import Formula

Challenge.LIMIT = 5

class ChallengeTestCase(WousoTest):
    def setUp(self):
        super(ChallengeTestCase, self).setUp()
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.chall_user = self.user.get_profile().get_extension(ChallengeUser)
        self.user2 = User.objects.create(username='_test2')
        self.user2.save()
        self.chall_user2 = self.user2.get_profile().get_extension(ChallengeUser)
        scoring.setup_scoring()
        ChallengeGame.get_instance().save()

    def tearDown(self):
        self.user.delete()
        self.user2.delete()

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

    def testUserCreate(self):
        user, new = User.objects.get_or_create(username='test2')

        profile = user.get_profile()

        self.assertTrue(isinstance(profile, Player))
        self.assertTrue(isinstance(profile.get_extension(ChallengeUser), ChallengeUser))

        user.delete()

    def testLaunch(self):
        Challenge.WARRANTY = False
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        self.assertTrue(isinstance(chall, Challenge))
        self.assertTrue(chall.is_launched())

        chall.refuse()
        self.assertTrue(chall.is_refused())
        chall.delete()

        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)
        chall.accept()
        self.assertTrue(chall.is_runnable())
        self.assertFalse(chall.is_refused())
        chall.delete()


    def test_run_accept(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.accept()
        self.assertTrue(chall.is_runnable())

    def test_run_is_started(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.accept()
        chall.set_start(self.chall_user)
        self.assertTrue(chall.is_started_for_user(self.chall_user))
        self.assertFalse(chall.is_started_for_user(self.chall_user2))

    @unittest.skip # TODO fixme
    def test_run_doesn_not_expires(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.accept()
        chall.set_start(self.chall_user)

        just_now = datetime.now()
        with patch('wouso.games.challenge.models.datetime') as mock_datetime:
            # after three minutes, challenge is still available
            mock_datetime.now.return_value = just_now + timedelta(minutes=3)
            #chall.set_played(self.chall_user, {})
            self.assertTrue(chall.is_expired_for_user(self.chall_user))
            # pass some more time, challenge cannot be submited any more
            mock_datetime.now.return_value = just_now + timedelta(minutes=10)
            self.assertFalse(chall.check_timedelta(self.chall_user))

    @unittest.skip
    def test_run_expires(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.accept()
        chall.set_start(self.chall_user)

        just_now = datetime.now()
        with patch('wouso.games.challenge.models.datetime') as mock_datetime:
            # after three minutes, challenge is still available
            mock_datetime.now.return_value = just_now + timedelta(minutes=5)
            self.assertTrue(chall.is_expired_for_user(self.chall_user))
            # pass some more time, challenge cannot be submited any more
            mock_datetime.now.return_value = just_now + timedelta(minutes=10)
            self.assertFalse(chall.check_timedelta(self.chall_user))

    def testScoring(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.user_from.seconds_took = 10
        chall.user_from.score = 100
        chall.user_from.save()
        chall.user_to.seconds_took = 10
        chall.user_to.score = 10
        chall.user_to.save()

        # TODO: improve usage of formulas inside tests.
        formula = Formula.get('chall-won')
        formula.definition = 'points=10 + min(10, int(3 * {winner_points}/{loser_points}))'
        formula.save()
        chall.played()

    def test_variable_timer(self):
        formula = Formula.add('chall-timer')
        formula.definition = 'tlimit=10'
        formula.save()

        self.assertEqual(scoring.timer(self.chall_user, ChallengeGame, 'chall-timer', level=self.chall_user.level_no), 10)

        formula.definition = 'tlimit={level}'
        formula.save()

        self.assertEqual(scoring.timer(self.chall_user, ChallengeGame, 'chall-timer', level=self.chall_user.level_no), self.chall_user.level_no)

class ChallengeApi(WousoTest):
    def setUp(self):
        super(ChallengeApi, self).setUp()
        Challenge.LIMIT = 5
        self.user = User.objects.create_user('_test', '', password='test')
        self.client.login(username='_test', password='test')

        self.user2 = User.objects.create_user('_test2', '', password='test')
        self.challuser = self.user.get_profile().get_extension(ChallengeUser)
        self.challuser2 = self.user2.get_profile().get_extension(ChallengeUser)
        ChallengeGame.get_instance().save()

    def test_list_active(self):
        response = self.client.get('/api/challenge/list/')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertFalse(data)

        # create an active challenge
        Formula.add('chall-warranty')
        chall = Challenge.create(user_from=self.challuser2, user_to=self.challuser, ignore_questions=True)
        response = self.client.get('/api/challenge/list/')
        data = json.loads(response.content)

        self.assertTrue(data)
        data = data[0]
        self.assertEqual(data['id'], chall.id)

    def test_get_challenge(self):
        # create an active challenge
        Formula.add('chall-warranty')
        Formula.add('chall-timer')
        chall = Challenge.create(user_from=self.challuser2, user_to=self.challuser, ignore_questions=True)
        chall.accept()
        response = self.client.get('/api/challenge/{id}/'.format(id=chall.id))
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertEqual(data['status'], 'A')
        self.assertEqual(data['to'], self.challuser.user.username)

    def test_post_challenge(self):
        # create an active challenge, with fake questions
        Formula.add('chall-warranty')
        Formula.add('chall-timer')
        category = Category.add('challenge')
        for i in range(Challenge.LIMIT + 1):
            q = Question.objects.create(text='text %s' % i, category=category, active=True)
            for j in range(5):
                Answer.objects.create(correct=j==1, question=q)
        chall = Challenge.create(user_from=self.challuser2, user_to=self.challuser)
        chall.accept()
        response = self.client.get('/api/challenge/{id}/'.format(id=chall.id))
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertEqual(data['status'], 'A')
        self.assertEqual(data['to'], self.challuser.user.username)
        self.assertEqual(len(data['questions']), Challenge.LIMIT)

        # attempt post
        data = {}
        for q in Question.objects.all():
            answers = []
            for a in q.correct_answers:
                answers.append(str(a.id))

            data[q.id] = ','.join(answers)

        response = self.client.post('/api/challenge/{id}/'.format(id=chall.id), data)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertTrue(data['success'])
        self.assertEqual(data['result']['points'], Challenge.LIMIT * 100)


class TestCalculatePoints(WousoTest):
    def get_question(self, correct_answers, wrong_answers):
        """ Create a question object with specific answers, first correct, then wrong
        """
        q = Question.objects.create(text='')
        for i in range(correct_answers):
            Answer.objects.create(question=q, correct=True, text='correct %d' % i)
        for i in range(wrong_answers):
            Answer.objects.create(question=q, correct=False, text='wrong %d' % i)
        return q

    def fake_answers(self, question, correct_answers, wrong_answers):
        """ Return a fake answers response, in the same format it is received with POST
        """
        post = {question.id: []}
        correct_answers_count = question.correct_answers.count()
        for i in range(correct_answers):
            post[question.id].append(question.answers[i].id)
        for i in range(wrong_answers):
            post[question.id].append(question.answers[i + correct_answers_count].id)
        return post

    def test_partial_correct_no_wrong(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 2, 0)
        self.assertEqual(Challenge._calculate_points(post)['points'], 50)

    def test_full_correct_no_wrong(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 4, 0)
        self.assertEqual(Challenge._calculate_points(post)['points'], 100)

    def test_partial_correct_and_wrong1(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 3, 2)
        self.assertEqual(Challenge._calculate_points(post)['points'], 8)

    def test_no_correct_and_partial_wrong(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 0, 2)
        self.assertEqual(Challenge._calculate_points(post)['points'], 0)

    def test_full_wrong(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 0, 3)
        self.assertEqual(Challenge._calculate_points(post)['points'], 0)

    def test_all_answers(self):
        q = self.get_question(4, 3)
        post = self.fake_answers(q, 4, 3)
        self.assertEqual(Challenge._calculate_points(post)['points'], 0)


class TestCustomChallenge(WousoTest):
    def test_custom_create(self):
        Challenge.WARRANTY = False
        game = ChallengeGame.get_instance()
        p1, p2 = self._get_player(1), self._get_player(2)

        challenge = Challenge.create_custom(p1, p2, [], game)
        self.assertTrue(challenge)
        self.assertEqual(challenge.owner, game)


class TestChallengeCache(WousoTest):
    def test_cache_points(self):
        scoring.setup_scoring()
        Challenge.WARRANTY = True
        p1, p2 = self._get_player(1), self._get_player(2)

        initial_points = p1.points
        challenge = Challenge.create(p1, p2, ignore_questions=True)
        p1 = Player.objects.get(pk=p1.pk)
        self.assertNotEqual(p1.points, initial_points)
        self.assertTrue(challenge)
        challenge.refuse()
        p1 = p1.user.get_profile()
        self.assertEqual(p1.points, initial_points)

# TODO: add page tests (views) for challenge run

