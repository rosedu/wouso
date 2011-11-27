import unittest
from datetime import datetime,timedelta
from mock import patch
from django.contrib.auth.models import User
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
        scoring.setup()

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

    def testRun(self):
        chall = Challenge.create(user_from=self.chall_user, user_to=self.chall_user2, ignore_questions=True)

        chall.accept()
        self.assertTrue(chall.is_runnable())

        chall.set_start(self.chall_user)
        self.assertTrue(chall.is_started_for_user(self.chall_user))
        self.assertFalse(chall.is_started_for_user(self.chall_user2))

        just_now = datetime.now()
        with patch('wouso.games.challenge.models.datetime') as mock_datetime:
            # after three minutes, challenge is still available
            mock_datetime.now.return_value = just_now + timedelta(minutes=3)
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

        formula = Formula.objects.get(id='chall-won')
        formula.formula = 'points=10 + min(10, int(3 * {winner_points}/{loser_points}))'
        formula.save()
        chall.played()