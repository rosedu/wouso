import os

from ckeditor.fields import RichTextField
from django.db import models
from django.conf import settings

from wouso.games.quiz.models import Quiz
from wouso.core.common import App


class LessonCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.CharField(max_length=1000, default="", blank=True)
    logo = models.ImageField(upload_to=settings.MEDIA_ARTIFACTS_DIR, null=True, blank=True)

    @property
    def logo_url(self):
        return os.path.join(settings.MEDIA_ARTIFACTS_URL, os.path.basename(str(self.logo))) if self.logo else ""

    @property
    def get_tags(self):
        """
        Get a list of all tags inside a category.
        If there is an order provided in self.order then the tags will be ordered accordingly,
        otherwise they will be in their natural order.
        Note: self.order contains a list of tag IDs separated by comma as a string.
        """
        if not self.order:
            return self.tags.all()

        order = [int(k) for k in self.order.split(',')]
        id_map = {}
        for tag in self.tags.all():
            id_map[tag.id] = tag

        tags_list = [id_map[k] for k in order]
        # Append any other remaining tags if there are
        tags_list.extend([tag for tag in self.tags.all() if tag not in tags_list])
        return tags_list

    def set_order(self, order):
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
    order = models.CharField(max_length=1000, default="", blank=True)
    logo = models.ImageField(upload_to=settings.MEDIA_ARTIFACTS_DIR, null=True, blank=True)

    @property
    def logo_url(self):
        return os.path.join(settings.MEDIA_ARTIFACTS_URL, os.path.basename(str(self.logo))) if self.logo else ""

    @property
    def number_of_lessons(self):
        return self.lessons.count()

    def get_lessons(self):
        """
        Get a list of all lessons (active + inactive) inside a tag.
        If there is an order provided in self.order then the lessons will be ordered accordingly,
        otherwise they will be in their natural order.
        Note: self.order contains a list of lesson IDs separated by comma as a string.
        """
        if not self.order:
            return self.lessons.all()

        order = [int(k) for k in self.order.split(',')]
        id_map = {}
        for lesson in self.lessons.all():
            id_map[lesson.id] = lesson

        lessons_list = [id_map[k] for k in order]
        # Append any other remaining lessons if there are
        lessons_list.extend([lesson for lesson in self.lessons.all() if lesson not in lessons_list])
        return lessons_list

    def get_active_lessons(self):
        return [l for l in self.get_lessons() if l.active]

    def set_order(self, order):
        self.order = ''
        for i in order:
            self.order += i + ','
        self.order = self.order[:-1]
        self.save()

    def __unicode__(self):
        return self.name


class Lesson(models.Model, App):
    """
     Lesson module
    """
    name = models.CharField(max_length=100)
    youtube_url = models.URLField(blank=True, null=True)
    content = RichTextField()
    tag = models.ForeignKey(LessonTag, blank=True, null=True, related_name='lessons', unique=True)
    quiz = models.ForeignKey(Quiz, blank=True, null=True)
    quiz_show_time = models.IntegerField(default=5)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name
