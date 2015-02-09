from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
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

        # Check the reset_reviews view
        admin = self._get_superuser()
        c = Client()
        c.login(username='admin', password='admin')
        # Create non expected review
        ar = Review.objects.create(answer=ans2, reviewer=p2, answer_grade=8)
        initial_reviews = len(Review.objects.all())
        response = c.get(reverse('ws_reset_assessment_reviews', args=[1, 2]))
        final_reviews = len(Review.objects.all())
        self.assertTrue(final_reviews < initial_reviews)
        self.assertEqual(response.status_code, 302)

        ans1.grade = 10
        ans1.save()
        r12.review_grade = 100
        r12.save()

        a1.update_grade()
        self.assertEqual(a1.grade, 10)
        self.assertEqual(a1.reviewer_grade, 200)
        self.assertEqual(a1.final_grade, 69)
        self.assertEqual(a1.reviews_grade, 3)

class TestWorkshopViews(WousoTest):
    def setUp(self):
        super(TestWorkshopViews, self).setUp()
        self.admin = self._get_superuser()
        self.c = Client()
        self.c.login(username='admin', password='admin')

    def test_add_group_view_get(self):
        response = self.c.get(reverse('ws_add_group'))
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Day')
        self.assertContains(response, 'Hour')
        self.assertContains(response, 'Room')

    def test_add_group_view_post(self):
        data = {u'room': u'ef108',
                u'name': u'semigroup_test',
                u'hour': u'10',
                u'day': u'1'}
        response = self.c.post(reverse('ws_add_group'), data)

        # Check if it redirects
        self.assertEqual(response.status_code, 302)

        # Check if it creates a semigroup
        self.assertTrue(Semigroup.objects.all())
        
        # Check if duplicates are created
        response = self.c.post(reverse('ws_add_group'), data)
        self.assertEqual(len(Semigroup.objects.all()), 1)

    def test_edit_group_view_get(self):
        sg = Semigroup.objects.create(day=u'1', hour=u'10', name=u'semigroup_test')
        response = self.c.get(reverse('ws_edit_group', args=[sg.pk]))
        self.assertContains(response, 'Name')
        self.assertContains(response, 'value="semigroup_test"')

    def test_edit_group_view_post(self):
        sg = Semigroup.objects.create(day=u'1', hour=u'10', name=u'semigroup_test')
        self.assertEqual(sg.room, u'eg306')
        data = {u'room': u'ef108',
                u'name': u'semigroup_test',
                u'hour': u'10',
                u'day': u'1'}
        response = self.c.post(reverse('ws_edit_group', args=[sg.pk]), data)
        sg = Semigroup.objects.get(name=u'semigroup_test')
        self.assertEqual(sg.room, u'ef108')

        # Check if user is redirected
        self.assertEqual(response.status_code, 302)

    def test_schedule_change_view_get(self):
        sch = Schedule.objects.create(name='schedule_test')
        # Get the response for editing a schedule URL:'schedule/edit/(?P<schedule>\d+)/'
        response = self.c.get(reverse('ws_schedule_change', args=[sch.pk]))
        self.assertContains(response, 'Name')
        self.assertContains(response, 'value="schedule_test"')

        # Get the response for adding a schedule URL:'schedule/add/'
        response = self.c.get(reverse('ws_schedule_change'))
        self.assertContains(response, 'Name')

    def test_schedule_change_view_post(self):
        today = datetime.today()
        sch = Schedule.objects.create(name='schedule_test')
        data = {u'name': u'schedule_new_name',
                u'start_date': today.date(),
                u'end_date': today.date(),
                u'count': 5}
        response = self.c.post(reverse('ws_schedule_change', args=[sch.pk]), data)
        sch = Schedule.objects.get(pk=sch.pk)
        self.assertEqual(sch.name, 'schedule_new_name')

    def test_workshop_add_view_get(self):
        response = self.c.get(reverse('ws_add_workshop'))
        self.assertContains(response, 'Semigroup')
        self.assertContains(response, 'Date')
        self.assertContains(response, 'Question count')

    def test_workshop_add_view_post(self):
        sg = Semigroup.objects.create(day=u'1', hour=u'10', name=u'semigroup_test')
        workshops = Workshop.objects.all()
        self.assertFalse(workshops)

        today = datetime.today()
        data = {u'semigroup': sg.id,
                u'date': today.date(),
                u'question_count': u'5'}
        response = self.c.post(reverse('ws_add_workshop'), data)
        workshops = Workshop.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(workshops), 1)

        # Check view without selecting a semigroup
        data = {u'semigroup': u'',
                u'date': today.date(),
                u'question_count': u'5'}
        response = self.c.post(reverse('ws_add_workshop'), data)
        self.assertContains(response, 'This field is required')

    def test_gradebook_view(self):
        sg = Semigroup.objects.create(day=u'1', hour=u'10', name=u'semigroup_test')
        pl1 = self._get_player(1)
        pl2 = self._get_player(2)
        sg.players.add(pl1, pl2)

        response = self.c.get(reverse('ws_gradebook', args=[sg.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')
