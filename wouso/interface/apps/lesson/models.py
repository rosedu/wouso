from ckeditor.fields import RichTextField
from django.db import models
from games.quiz.models import Quiz


class LessonCategory(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Lesson(models.Model):
    """
     The lesson
    """
    name = models.CharField(max_length=100)
    content = RichTextField()
    category = models.ForeignKey(LessonCategory)
    quiz = models.ForeignKey(Quiz)
    quiz_show_time = models.IntegerField(default=5)

    def __unicode__(self):
        return self.name
