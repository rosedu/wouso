from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from models import *

class TestWorkshop(TestCase):

    def test_current_spot_semigroup(self):
        now = datetime.now()
        hour = now.hour - now.hour % 2
        group = Semigroup.objects.create(name='test', day=now.weekday() + 1, hour=hour)

        spot_day, spot_hour = WorkshopGame.get_spot(timestamp=now)
        self.assertEqual(spot_day, group.day)
        self.assertEqual(spot_hour, group.hour)

        self.assertEqual(WorkshopGame.get_semigroup(timestamp=now), group)

    def test_get_workshop_always(self):
        now = datetime.now()
        hour = now.hour - now.hour % 2
        group = Semigroup.objects.create(name='test', day=now.weekday() + 1, hour=hour)

        # Create a tag, question and schedule it now
        tag = Schedule.objects.create(name='test-tag', start_date=now, end_date=now + timedelta(days=1))
        question = Question.objects.create()
        question.tags.add(tag)

        ws = WorkshopGame.get_for_now(timestamp=now, always=True)

        self.assertTrue(ws)

    def test_start_reviewing(self):
        now = datetime.now()
        hour = now.hour - now.hour % 2
        group = Semigroup.objects.create(name='test', day=now.weekday() + 1, hour=hour)

        ws = Workshop.objects.create(semigroup=group, date=now.date())

        # Two players
        u1 = User.objects.create(username='u1').get_profile()
        u2 = User.objects.create(username='u2').get_profile()

        a1 = Assesment.objects.create(player=u1, workshop=ws)
        a2 = Assesment.objects.create(player=u2, workshop=ws)

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