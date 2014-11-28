from ckeditor.fields import RichTextField
from django.db import models
from games.quiz.models import Quiz


class LessonCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.CharField(max_length=1000, default="", blank=True)

    @property
    def lessons(self):
        """ Get lessons in specified order """
        if not self.order:
            return self.lesson_set.all()
        else:
            order = [int(i) for i in self.order.split(',')]
            ls = {}
            for l in self.lesson_set.all():
                ls[l.id] = l
            return [ls[i] for i in order]

    @property
    def active_lessons(self):
        return [l for l in self.lessons if l.active]

    def reorder(self, order):
        self.order = ''
        for i in order:
            self.order += i + ','
        self.order = self.order[:-1]
        self.save()

    def __unicode__(self):
        return self.name


class Lesson(models.Model):
    """
     The lesson
    """
    name = models.CharField(max_length=100)
    youtube_url = models.URLField(blank=True, null=True)
    content = RichTextField()
    category = models.ForeignKey(LessonCategory)
    quiz = models.ForeignKey(Quiz, blank=True, null=True)
    quiz_show_time = models.IntegerField(default=5)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name
