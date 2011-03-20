import unittest
from django.contrib.auth.models import User
from models import *
from wouso.core.qpool import get_questions_with_tags

class QpoolTestCase(unittest.TestCase):
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
        self.question.add_tag(tag)
        
        self.assertTrue(self.question.has_tag('test'))
        self.assertTrue(self.question in get_questions_with_tags('test'))
        self.assertTrue(self.question in get_questions_with_tags(['test']))
        self.assertTrue(self.question not in get_questions_with_tags('inexistent'))
        
        # check multiple
        tag2 = Tag.objects.create(name='other')
        tag2.save()
        self.question.add_tag(tag2)
        
        self.assertTrue(self.question.has_tag('other'))
        self.assertTrue(self.question in get_questions_with_tags(['test', 'other']))
        self.assertTrue(self.question not in get_questions_with_tags(['test', 'inexistent'], 'all'))
        self.assertTrue(self.question not in get_questions_with_tags(['coco', 'test'], 'all'))
