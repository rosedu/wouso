from ckeditor.fields import RichTextField
from django.db import models
from wouso.games.quiz.models import Quiz
from wouso.core.common import App


class LessonCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.CharField(max_length=1000, default="", blank=True)

    @property
    def lessons(self):
        """ Get lessons in specified order """
        if not self.order:
            return self.get_unordered_lessons()
        else:
            order = [int(i) for i in self.order.split(',')]
            ls = {}
            for l in self.get_unordered_lessons():
                ls[l.id] = l
            first = [ls[i] for i in order]
            full_ls = []
            full_ls.extend(first)
            for l in self.get_unordered_lessons():
                if l not in first:
                    full_ls.append(l)
            return full_ls

    @property
    def active_lessons(self):
        return [l for l in self.lessons if l.active]

    def get_unordered_lessons(self):
        lessons = []
        for t in self.tags.all():
            for l in t.lessons.all():
                lessons.append(l)
        return lessons

    def reorder(self, order):
        self.order = ''
        for i in order:
            self.order += i + ','
        self.order = self.order[:-1]
        self.save()

    def __unicode__(self):
        return self.name


class LessonTag(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(LessonCategory, blank=True, null=True, related_name='tags')

    @property
    def number_of_lessons(self):
        return self.lessons.count()

    @property
    def active_lessons(self):
        return [l for l in self.category.active_lessons if l.tag.name == self.name]

    def __unicode__(self):
        return self.name


class Lesson(models.Model, App):
    """
     Lesson module
    """
    name = models.CharField(max_length=100)
    youtube_url = models.URLField(blank=True, null=True)
    content = RichTextField()
    tag = models.ForeignKey(LessonTag, blank=True, null=True, related_name='lessons')
    quiz = models.ForeignKey(Quiz, blank=True, null=True)
    quiz_show_time = models.IntegerField(default=5)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name
