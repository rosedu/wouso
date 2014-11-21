from ckeditor.fields import RichTextField
from django.db import models
from games.quiz.models import Quiz


class LessonCategory(models.Model):
    name = models.CharField(max_length=100)

    @property
    def lessons(self):
        return self.lesson_set.all()

    def __unicode__(self):
        return self.name


class Lesson(models.Model):
    """
     The lesson
    """
    name = models.CharField(max_length=100)
    youtube_url = models.URLField()
    content = RichTextField()
    category = models.ForeignKey(LessonCategory)
    quiz = models.ForeignKey(Quiz, blank=True, null=True)
    quiz_show_time = models.IntegerField(default=5)

    def __unicode__(self):
        return self.name
