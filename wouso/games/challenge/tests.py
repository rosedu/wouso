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
from wouso.games.challenge.models import ChallengeUser, Challenge, ChallengeGame
from wouso.core.user.models import Player, Race
from wouso.core import scoring
from wouso.core.scoring.models import Formula, Coin
from wouso.games.challenge.views import challenge_random, launch
from wouso.interface.top.models import Top, TopUser, History

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

    @unittest.skip  # TODO fixme
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

    @unittest.skip  # TODO fixme
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
        formula.expression = 'points=10 + min(10, int(3 * {winner_points}/{loser_points}))'
        formula.save()
        chall.played()

    def test_scoring_win(self):
        initial_points = 10
        winner = self._get_player(1).get_extension(ChallengeUser)
        loser = self._get_player(2).get_extension(ChallengeUser)

        # Setup scoring
        scoring.setup_scoring()
        Coin.add('points')

        # Give initial points
        scoring.score_simple(winner, 'points', initial_points)
        scoring.score_simple(loser, 'points', initial_points)

        # Set formula
        win_points = 6
        formula = Formula.get('chall-won')
        formula.expression = 'points=' + str(win_points)
        formula.save()

        # Play challenge
        chall = Challenge.create(user_from=winner, user_to=loser, ignore_questions=True)
        chall.set_won_by_player(winner)

        self.assertEqual(winner.player_ptr.points, initial_points + win_points)

    def test_scoring_loss(self):
        initial_points = 10
        winner = self._get_player(1).get_extension(ChallengeUser)
        loser = self._get_player(2).get_extension(ChallengeUser)

        # Setup scoring
        scoring.setup_scoring()
        Coin.add('points')

        # Give initial points
        scoring.score_simple(winner, 'points', initial_points)
        scoring.score_simple(loser, 'points', initial_points)

        # Set formula
        loss_points = -2
        formula = Formula.get('chall-lost')
        formula.expression = 'points=' + str(loss_points)
        formula.save()

        # Play challenge
        chall = Challenge.create(user_from=winner, user_to=loser, ignore_questions=True)
        chall.set_won_by_player(winner)

        self.assertEqual(loser.player_ptr.points, initial_points + loss_points) # loss_points is negative

    def test_variable_timer(self):
        formula = Formula.add('chall-timer')
        formula.expression = 'tlimit=10'
        formula.save()

        self.assertEqual(scoring.timer(self.chall_user, ChallengeGame, 'chall-timer', level=self.chall_user.level_no), 10)

        formula.expression = 'tlimit={level}'
        formula.save()

        self.assertEqual(scoring.timer(self.chall_user, ChallengeGame, 'chall-timer', level=self.chall_user.level_no), self.chall_user.level_no)

    def test_in_same_division(self):
        n = 100
        points_offset = 10000
        division_range = 20

        players = [self._get_player(i).get_extension(ChallengeUser) for i in xrange(n)]

        # Add an offset value to every user's points in order to avoid top overlapping with other test users.
        for i in xrange(n):
            scoring.score_simple(players[i], 'points', points_offset + i * 10)

        # Update players top.
        for i, u in enumerate(Player.objects.all().order_by('-points')):
            topuser = u.get_extension(TopUser)
            position = i + 1
            hs, created = History.objects.get_or_create(user=topuser, date=datetime.now().date(), relative_to=None)
            hs.position, hs.points = position, u.points
            hs.save()

        # Check first player.
        self.assertTrue(players[n-1].in_same_division(players[n-2]))
        self.assertTrue(players[n-1].in_same_division(players[max(0, n-1-division_range)]))

        # Check last player.
        self.assertTrue(players[0].in_same_division(players[1]))
        self.assertTrue(players[0].in_same_division(players[min(n-1, division_range)]))

        # Check middle player.
        t = n / 2
        self.assertTrue(players[t].in_same_division(players[max(0, t-division_range)]))
        self.assertTrue(players[t].in_same_division(players[min(n-1, t+division_range)]))
        self.assertTrue(players[t].in_same_division(players[t-1]))
        self.assertTrue(players[t].in_same_division(players[t+1]))

    def test_not_in_same_division(self):
        n = 100
        points_offset = 10000
        division_range = 20

        players = [self._get_player(i).get_extension(ChallengeUser) for i in xrange(n)]

        # Add an offset value to every user's points in order to avoid top overlapping with other test users.
        for i in xrange(n):
            scoring.score_simple(players[i], 'points', points_offset + i*10)

        # Update players top.
        for i, u in enumerate(Player.objects.all().order_by('-points')):
            topuser = u.get_extension(TopUser)
            position = i + 1
            hs, created = History.objects.get_or_create(user=topuser, date=datetime.now().date(), relative_to=None)
            hs.position, hs.points = position, u.points
            hs.save()

        # Check first player.
        self.assertFalse(players[n-1].in_same_division(players[max(0, n-1-division_range-1)]))

        # Check last player.
        self.assertFalse(players[0].in_same_division(players[min(n-1, division_range+1)]))

        # Check middle player.
        t = n / 2
        self.assertFalse(players[t].in_same_division(players[max(0, t-division_range-1)]))
        self.assertFalse(players[t].in_same_division(players[min(n-1, t+division_range+1)]))


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

class TestChallengeViews(WousoTest):
    def setUp(self):
        super(TestChallengeViews, self).setUp()
        self.ch_player1 = self._get_player(1)
        self.ch_player2 = self._get_player(2)
        race = Race.objects.create(name=u'testrace', can_play=True)
        self.ch_player1.race = race
        self.ch_player2.race = race
        self.ch_player1.points = 100
        self.ch_player2.points = 100
        self.ch_player1.save()
        self.ch_player2.save()
        self.ch_player1 = self.ch_player1.get_extension(ChallengeUser)
        self.ch_player2 = self.ch_player2.get_extension(ChallengeUser)
        scoring.setup_scoring()

        self.category = Category.add('challenge')
        self.question1 = Question.objects.create(text='question1', answer_type='F',
                                                 category=self.category, active=True)
        self.answer1 = Answer.objects.create(text='first answer', correct=True,
                                             question=self.question1)
        self.question2 = Question.objects.create(text='question2', answer_type='F',
                                                 category=self.category, active=True)
        self.answer2 = Answer.objects.create(text='second answer', correct=True,
                                             question=self.question2)
        self.ch = Challenge.create(user_from=self.ch_player1, user_to=self.ch_player2,
                        ignore_questions=True)
        self.ch.questions.add(self.question1)
        self.ch.questions.add(self.question2)

        self.c = Client()
        self.c.login(username='testuser1', password='test')

    def test_challenge_index(self):
        Challenge.create(user_from=self.ch_player2, user_to=self.ch_player1,
                        ignore_questions=True)
        response = self.c.get(reverse('challenge_index_view'))
        # Test if both challenges are displayed
        self.assertContains(response, 'testuser1</a> vs')
        self.assertContains(response, 'testuser2</a> vs')

    def test_challenge_is_not_runnable_when_it_is_not_accepted(self):
        # Challenge is launched but not accepted
        self.ch.status = 'L'
        self.ch.save()
        response = self.c.get(reverse('view_challenge', args=[self.ch.id]), follow=True)
        self.assertContains(response, _('The challenge was not accepted'))

    def test_challenge_is_not_runnable_when_it_is_refused(self):
        # Challenge is refused
        self.ch.status = 'R'
        self.ch.save()
        response = self.c.get(reverse('view_challenge', args=[self.ch.id]), follow=True)
        self.assertContains(response, _('The challenge was refused'))

    def test_challenge_is_not_runnable_more_than_once(self):
        self.ch.status = 'A'
        self.ch.save()
        participant = self.ch.participant_for_player(self.ch_player1)
        participant.played = True
        participant.score = 200
        participant.save()
        response = self.c.get(reverse('view_challenge', args=[self.ch.id]), follow=True)
        self.assertContains(response, _('You have already submitted this challenge'))

    def test_challenge_is_runnable(self):
        # Challenge is accepted, display the challenge
        self.ch.status = 'A'
        self.ch.save()
        response = self.c.get(reverse('view_challenge', args=[self.ch.id]))
        self.assertContains(response, 'first answer')
        self.assertContains(response, 'second answer')

    def test_challenge_can_be_submitted_only_once(self):
        self.ch.status = 'A'
        self.ch.save()
        # Run the challenge
        response = self.c.get(reverse('view_challenge', args=[self.ch.id]))
        # Submit the challenge
        data = {self.question1.id: [u'answer_%d' %(self.answer1.id)],
                self.question2.id: [u'answer_%d' %(self.answer2.id)]}
        response = self.c.post(reverse('view_challenge', args=[self.ch.id]), data)
        self.assertContains(response, 'You scored')
        # Try to submit it again
        response = self.c.post(reverse('view_challenge', args=[self.ch.id]), data, follow=True)
        self.assertContains(response, 'You have already submitted')

    def test_challenge_cannot_be_submitted_when_it_is_not_accepted(self):
        self.ch.status = 'L'
        self.ch.save()
        # Submit the challenge
        data = {self.question1.id: [u'answer_%d' %(self.answer1.id)],
                self.question2.id: [u'answer_%d' %(self.answer2.id)]}
        response = self.c.post(reverse('view_challenge', args=[self.ch.id]), data, follow=True)
        self.assertContains(response, 'The challenge was not accepted')

    def test_challenge_cannot_be_submitted_when_it_is_refused(self):
        self.ch.status = 'R'
        self.ch.save()
        # Submit the challenge
        data = {self.question1.id: [u'answer_%d' %(self.answer1.id)],
                self.question2.id: [u'answer_%d' %(self.answer2.id)]}
        response = self.c.post(reverse('view_challenge', args=[self.ch.id]), data, follow=True)
        self.assertContains(response, 'The challenge was refused')

    def test_challenge_history(self):
        self.ch.status = 'A'
        self.ch.save()
        response = self.c.get(reverse('challenge_history', args=[self.ch_player1.id]))
        self.assertContains(response, 'testuser1</a> vs.')
        self.assertContains(response, 'Result:')
        self.assertContains(response, 'Pending [A]')

    def test_random_challenge(self):
        # Add 3 more questions because when the player is challenged
        # ignore_questions is set to False and the challenge needs 5 questions
        question3 = Question.objects.create(text='question3', answer_type='F',
                                                 category=self.category, active=True)
        question4 = Question.objects.create(text='question4', answer_type='F',
                                                 category=self.category, active=True)
        question5 = Question.objects.create(text='question5', answer_type='F',
                                                 category=self.category, active=True)
        self.c.login(username='testuser2', password='test')
        response = self.c.get(reverse('challenge_random'), follow=True)
        challenge = Challenge.objects.filter(user_from__user__user__username='testuser2')
        self.assertNotEqual(len(challenge), 0)

    def test_detailed_challenge_stats_view_mine(self):
        self.ch.status = 'A'
        self.ch.save()

        self.ch.user_from.seconds_took = 100
        self.ch.user_from.score = 200
        self.ch.user_from.save()

        self.ch.user_to.score = 300
        self.ch.user_to.seconds_took = 50
        self.ch.user_to.save()

        response = self.c.get(reverse('detailed_challenge_stats', args=[self.ch_player2.id]))
        self.assertContains(response, 'testuser1 - testuser2')
        self.assertContains(response, '100')
        self.assertContains(response, '200')
        self.assertContains(response, '300')
        self.assertContains(response, '50')

    def test_detailed_challenge_stats_view(self):
        admin = User.objects.create_superuser('admin', 'admin@myemail.com', 'admin')
        self.c.login(username='admin', password='admin')
        self.ch.status = 'A'
        self.ch.save()

        self.ch.user_from.seconds_took = 100
        self.ch.user_from.score = 200
        self.ch.user_from.save()

        self.ch.user_to.score = 300
        self.ch.user_to.seconds_took = 50
        self.ch.user_to.save()

        response = self.c.get(reverse('detailed_challenge_stats', args=[self.ch_player2.id, self.ch_player1.id]))
        self.assertContains(response, 'testuser2 - testuser1')
        self.assertContains(response, '100')
        self.assertContains(response, '200')
        self.assertContains(response, '300')
        self.assertContains(response, '50')

    def test_challenge_stats_view_mine(self):
        self.ch.status = 'A'
        self.ch.save()
        self.ch.user_from.seconds_took = 100
        self.ch.user_from.save()
        response = self.c.get(reverse('challenge_stats'))
        self.assertContains(response, 'Challenges - testuser1')
        self.assertContains(response, 'Challenges played:  1')
        self.assertContains(response, 'Challenges sent:  1')
        self.assertContains(response, 'testuser2')
        self.assertContains(response, 'Average time taken:  100.0 s')

    def test_challenge_stats_view(self):
        admin = User.objects.create_superuser('admin', 'admin@myemail.com', 'admin')
        self.c.login(username='admin', password='admin')

        self.ch.status = 'A'
        self.ch.save()
        self.ch.user_to.seconds_took = 100
        self.ch.user_to.save()
        response = self.c.get(reverse('challenge_stats', args=[self.ch_player2.id]))
        self.assertContains(response, 'Challenges - testuser2')
        self.assertContains(response, 'Challenges played:  1')
        self.assertContains(response, 'Challenges sent:  0')
        self.assertContains(response, 'testuser1')

    def test_challenge_button_display(self):
        response = self.c.get(reverse('player_profile', args=[self.ch_player1.pk]))

        # Button is not displayed for the user who is making the request
        self.assertNotContains(response, _('Challenge!'))

        # Button is deactivated when a challenge is already launched
        response = self.c.get(reverse('player_profile', args=[self.ch_player2.pk]))
        self.assertContains(response, _('Challenged'))

        # Button is displayed for a different user
        self.c.login(username='testuser2', password='test')
        response = self.c.get(reverse('player_profile', args=[self.ch_player1.pk]))
        self.assertContains(response, _('Challenge'))

    def test_admin_button_challenges(self):
        admin = self._get_superuser()
        url = reverse('challenge_stats', args=[self.ch_player2.pk])

        # Button is not displayed for normal users
        response = self.c.get(reverse('player_profile', args=[self.ch_player2.pk]))
        self.assertNotContains(response,
                    '<a class="button" href="%s">%s</a>' % (url, _('Challenges')))

        # Button is displayed for super users
        self.c.login(username=admin.username, password='admin')
        response = self.c.get(reverse('player_profile', args=[self.ch_player2.pk]))
        self.assertContains(response,
                    '<a class="button" href="%s">%s</a>' % (url, _('Challenges')))

