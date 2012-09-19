from django.test import TestCase
from django.contrib.auth.models import User
from models import *
from wouso.core.qpool import get_questions_with_tags

class QpoolTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='_test')
        self.user.save()
        self.question = self._get_foo_question()
        
    def tearDown(self):
        self.user.delete()
        self.question.delete()
        
    def _get_foo_question(self):
        q = Question.objects.create(text='Cati ani ai',
            proposed_by=self.user,
            endorsed_by=self.user,
            active=True)
        q.save()
        answers = [Answer.objects.create(question=q, 
            text=str(i),
            correct=False if i != 2 else True) for i in range(4)]
        [a.save() for a in answers]
        return q
        
    def testQuestionAdd(self):
        q = self.question
        
        self.assertTrue(isinstance(q, Question))
        self.assertEqual(q.answers.count(), 4)
        self.assertTrue(q.is_valid())
    
    def testQuestionTag(self):
        tag = Tag.objects.create(name='test')
        tag.save()
        self.question.tags.add(tag)
        
        self.assertTrue(self.question in get_questions_with_tags('test'))
        self.assertTrue(self.question in get_questions_with_tags(['test']))
        self.assertTrue(self.question not in get_questions_with_tags('inexistent'))
        
        # check multiple
        tag2 = Tag.objects.create(name='other')
        tag2.save()
        self.question.tags.add(tag2)
        
        self.assertTrue(self.question in get_questions_with_tags(['test', 'other']))
        self.assertTrue(self.question not in get_questions_with_tags(['test', 'inexistent'], 'all'))
        self.assertTrue(self.question not in get_questions_with_tags(['coco', 'test'], 'all'))

class TagTests(TestCase):
    def test_tag_set_active(self):
        q = Question.objects.create()
        t = Tag.objects.create()
        q.tags.add(t)

        t.set_active()
        q = Question.objects.get(pk=q.id)
        self.assertTrue(q.active)

    def test_tag_set_inactive(self):
        q = Question.objects.create()
        t = Tag.objects.create()
        q.tags.add(t)

        q.active = True
        q.save()
        t.active = True
        t.save()

        t.set_inactive()

        q = Question.objects.get(pk=q.id)
        self.assertFalse(q.active)

class QuestionTest(TestCase):
    def test_question_schedule(self):
        q = Question.objects.create()

        self.assertFalse(q.day)
        self.assertEqual(q.scheduled, '-')

        s = Schedule.objects.create(question=q)

        self.assertTrue(q.day)

        self.assertEqual(q.scheduled, str(q.day))

    def test_question_valid(self):
        q = Question.objects.create()

        self.assertEqual(q.type, 'S')
        self.assertFalse(q.is_valid())

        Answer.objects.create(question=q, correct=True)
        self.assertTrue(q.is_valid())

        q.type = 'F'
        q.save()

        self.assertFalse(q.text)
        self.assertFalse(q.is_valid())

        q.text = 'some text'
        q.save()
        self.assertTrue(q.is_valid())

    def test_question_tag(self):
        q = Question.objects.create()

        self.assertEqual(q.tags_nice, '')

        t = Tag.objects.create(name='name')

        q.tags.add(t)
        self.assertEqual(q.tags_nice, 'name')

class ScheduleTest(TestCase):
    def test_schedule_automatic(self):
        cat = Category.objects.create(name='qotd')
        q = Question.objects.create(active=True, category=cat)

        self.assertFalse(q.day)
        Schedule.automatic(qotd='qotd')
        self.assertTrue(q.day)