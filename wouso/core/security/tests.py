from django.contrib.auth.models import User
from wouso.games.challenge.models import Challenge, ChallengeUser
from wouso.core.tests import WousoTest
from wouso.core import scoring


class SecurityRulesTest(WousoTest):
    def setUp(self):
        super(SecurityRulesTest, self).setUp()
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.chall_user = self.user.get_profile().get_extension(ChallengeUser)
        self.user2 = User.objects.create(username='_test2')
        self.user2.save()
        self.chall_user2 = self.user2.get_profile().get_extension(ChallengeUser)
        scoring.setup_scoring()

    def test_rule_challenge_was_set_up(self):
        #run a challenge
        Challenge.WARRANTY = False
        chall = Challenge.create(user_from=self.chall_user,
                                 user_to=self.chall_user2, ignore_questions=True)

        chall.user_from.seconds_took = 10
        chall.user_from.score = 100
        chall.user_from.save()
        chall.user_to.seconds_took = 10
        chall.user_to.score = 10
        chall.user_to.save()
        chall.played()

        #test penalty points
        #20 is the default formula value for a chall-was-set-up
        self.assertEqual(20,
                         scoring.History.user_coins(self.user2.player_related.get())['penalty'])
