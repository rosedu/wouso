from nose.tools import raises
from django.db import IntegrityError
from django.test import TestCase

from wouso.interface.apps.lesson.models import LessonCategory, LessonTag, Lesson

class LessonCategoryTestCase(TestCase):  

    @raises(IntegrityError)
    def test_lesson_cateory_name_is_unique(self):
        lesson_category1 = LessonCategory.objects.create(name='a')
        lesson_category2 = LessonCategory.objects.create(name='a')
        lesson_category1.save()
        lesson_category2.save()


class LessonTestCase(TestCase):  

    @raises(IntegrityError)
    def test_lesson_tag_is_unique(self):
        lesson_tag = LessonTag.objects.create()	
        lesson = Lesson.objects.create(tag=lesson_tag)
        lesson2 = Lesson.objects.create(tag=lesson_tag)
        lesson1.save()
        lesson2.save()
