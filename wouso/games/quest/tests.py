from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from wouso.core import scoring
from wouso.core.qpool.models import Question, Answer, Category
from models import *

class QuestTestCase(TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.quest_user = profile.get_extension(QuestUser)
        scoring.setup_scoring()

    def tearDown(self):
        #self.user.delete()
        pass

    def check_answer_test(self):
        cat = Category.objects.create(name='quest')
        question = Question.objects.create(text='test_q', answer_type='F',
                                           category=cat, active=True)
        answer1 = Answer.objects.create(text='test_a1', correct=True, question=question)
        answer2 = Answer.objects.create(text='test_a2', correct=True, question=question)

        start = datetime.datetime.now()
        end = datetime.datetime.now() + timedelta(days=1)
        quest = Quest.objects.create(start=start, end=end)

        quest.questions.add(question)

        self.assertEqual(quest.count, 1)

        self.quest_user.current_quest = quest

        quest.check_answer(self.quest_user, 'Test_a2')

        self.assertTrue(self.quest_user.finished)

