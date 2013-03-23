from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from models import *
from wouso.core.tests import WousoTest

class TestWorkshop(TestCase):

    def test_current_spot_semigroup(self):
        now = datetime.now()
        hour = now.hour - now.hour % 2
        group = Semigroup.objects.create(name='test', day=now.weekday() + 1, hour=hour)

        spot_day, spot_hour = WorkshopGame.get_spot(timestamp=now)
        self.assertEqual(spot_day, group.day)
        self.assertEqual(spot_hour, group.hour)

        self.assertEqual(WorkshopGame.get_semigroups(timestamp=now)[0], group)

    def test_start_reviewing(self):
        now = datetime.now()
        hour = now.hour - now.hour % 2
        group = Semigroup.objects.create(name='test', day=now.weekday() + 1, hour=hour)

        ws = Workshop.objects.create(semigroup=group, date=now.date())

        # Two players
        u1 = User.objects.create(username='u1').get_profile()
        u2 = User.objects.create(username='u2').get_profile()

        a1 = Assessment.objects.create(player=u1, workshop=ws, answered=True)
        a2 = Assessment.objects.create(player=u2, workshop=ws, answered=True)

        WorkshopGame.start_reviewing(ws)

        # Test reviewers: one reviews another
        self.assertTrue(u1 in a2.reviewers.all())
        self.assertTrue(u2 in a1.reviewers.all())

        # Test info
        i1 = WorkshopGame.get_player_info(u1, ws)
        i2 = WorkshopGame.get_player_info(u2, ws)

        self.assertTrue(i1['participated'])
        self.assertTrue(i2['participated'])

        # TODO: add some answers and test positive values here
        self.assertEqual(i1['expected_reviews'].count(), 0)
        self.assertEqual(i2['expected_reviews'].count(), 0)

        self.assertEqual(i1['reviews'].count(), 0)
        self.assertEqual(i2['reviews'].count(), 0)

class TestAssessment(WousoTest):
    def test_grading(self):
        p1 = self._get_player(1)
        p2 = self._get_player(2)
        semig = Semigroup.objects.create(day=datetime.today().day, hour=datetime.today().hour - datetime.today().hour % 2)
        semig.players.add(p1, p2)

        s = Schedule.objects.create(count=4)
        for i in range(4):
            q = Question.objects.create()
            q.tags.add(s)

        self.assertTrue(s.is_active())

        w = Workshop.objects.create(semigroup=semig)
        self.assertTrue(w.is_ready())

        w.start()

        a1 = w.get_or_create_assessment(p1)
        a2 = w.get_or_create_assessment(p2)

        self.assertFalse(a1.answered)
        self.assertFalse(a2.answered)

        # Check questions
        self.assertEqual(a1.questions.all().count(), 4)
        #self.assertEqual(a1.questions.all()[-1], q)

        a1.set_answered()
        a2.set_answered()

        w.stop()

        self.assertTrue(a1.answered)
        self.assertTrue(a2.answered)

        WorkshopGame.start_reviewing(w)

        self.assertIn(p2, a1.reviewers.all())
        self.assertIn(p1, a2.reviewers.all())

        ans1 = Answer.objects.get(question=q, assessment=a1)
        ans2 = Answer.objects.get(question=q, assessment=a2)

        r21 = Review.objects.create(answer=ans1, reviewer=p2, answer_grade=3)
        self.assertEqual(a1.reviews_grade, 3)

        r12 = Review.objects.create(answer=ans2, reviewer=p1, answer_grade=7)
        self.assertEqual(a2.reviews_grade, 7)

        ar = Review.objects.create(answer=ans2, reviewer=p2, answer_grade=8)
        self.assertEqual(a2.reviews_grade, 7) # ignores reviews from non-reviewers
        ar.delete()

        ans1.grade = 10
        ans1.save()
        r12.review_grade = 100
        r12.save()

        a1.update_grade()
        self.assertEqual(a1.grade, 10)
        self.assertEqual(a1.reviewer_grade, 200)
        self.assertEqual(a1.final_grade, 69)
        self.assertEqual(a1.reviews_grade, 3)