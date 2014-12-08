from ckeditor.fields import RichTextField
from django.db import models
from wouso.core.user.models import Player


class ForumUser(Player):
    def __unicode__(self):
        return self.full_name


Player.register_extension('top', ForumUser)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Forum(models.Model):
    category = models.ForeignKey('Category')
    name = models.CharField(blank=True, max_length=255)
    position = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    is_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Topic(models.Model):
    forum = models.ForeignKey(Forum)
    name = models.CharField(max_length=255)
    last_post = models.ForeignKey('Post', verbose_name='Last post',
                                  related_name='forum_last_post',
                                  blank=True, null=True)

    class Meta:
        ordering = ['-last_post__created']

    def __unicode__(self):
        return self.name


class Post(models.Model):
    topic = models.ForeignKey(Topic)
    user = models.ForeignKey(ForumUser)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    indentation = models.IntegerField(default=0)
    text = RichTextField()

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.text
