import os
from django.test import TestCase
from wouso.core.qpool.models import Question
from import_questions import import_from_file, add


class ImportQuestion(TestCase):
    def test_import_questions(self):
        self.assertEqual(Question.objects.all().count(), 0)
        contrib = os.path.join(os.path.dirname(__file__), '../../contrib/')
        with open(contrib + 'questions.txt', 'r') as f:
            count = import_from_file(f)

        self.assertEqual(count, 22)
        self.assertEqual(Question.objects.all().count(), 22)


    def test_add_question(self):
        question = add({'text': "Question text"}, [{'text': 'answer 1'}])

        self.assertTrue(question)

        self.assertEqual(question.text, "Question text")
        self.assertEqual(question.answers.count(), 1)