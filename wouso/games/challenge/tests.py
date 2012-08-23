import json
import unittest
from datetime import datetime,timedelta
from mock import patch

from django.test.testcases import TestCase
from django.contrib.auth.models import User
from wouso.core.qpool.models import Question, Answer, Category
from wouso.games.challenge.models import ChallengeUser, Challenge, ChallengeGame
from wouso.core.user.models import Player
from wouso.core import scoring
from wouso.core.scoring.models import Formula

class ChallengeTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.chall_user = self.user.get_profile().get_extension(ChallengeUser)
        self.user2 = User.objects.create(username='_test2')
        self.user2.save()
        self.chall_user2 = self.user2.get_profile().get_extension(ChallengeUser)
        scoring.setup_scoring()

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
        formula = Formula.objects.get(id='chall-won')
        formula.formula = 'points=10 + min(10, int(3 * {winner_points}/{loser_points}))'
        formula.save()
        chall.played()

class ChallengeApi(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('_test', '', password='test')
        self.client.login(username='_test', password='test')

        self.user2 = User.objects.create_user('test2', '', password='test')
        self.challuser = self.user.get_profile().get_extension(ChallengeUser)
        self.challuser2 = self.user2.get_profile().get_extension(ChallengeUser)

    def test_list_active(self):
        response = self.client.get('/api/challenge/list/')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertFalse(data)

        # create an active challenge
        Formula.objects.create(id='chall-warranty')
        chall = Challenge.create(user_from=self.challuser2, user_to=self.challuser, ignore_questions=True)
        response = self.client.get('/api/challenge/list/')
        data = json.loads(response.content)

        self.assertTrue(data)
        data = data[0]
        self.assertEqual(data['id'], chall.id)

    def test_get_challenge(self):
        # create an active challenge
        Formula.objects.create(id='chall-warranty')
        chall = Challenge.create(user_from=self.challuser2, user_to=self.challuser, ignore_questions=True)
        chall.accept()
        response = self.client.get('/api/challenge/{id}/'.format(id=chall.id))
        data = json.loads(response.content)

        self.assertTrue(data)
        self.assertEqual(data['status'], 'A')
        self.assertEqual(data['to'], self.challuser.user.username)

    def test_post_challenge(self):
        # create an active challenge, with fake questions
        Formula.objects.create(id='chall-warranty')
        category = Category.objects.create(name='challenge')
        for i in range(5):
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
        self.assertEqual(len(data['questions']), 5)

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
        self.assertEqual(data['result']['points'], 500)
