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
    category = models.ForeignKey('Category', related_name='forums')
    name = models.CharField(blank=True, max_length=255)
    position = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    is_closed = models.BooleanField(default=False)

    @property
    def last_topic(self):
        if self.topics.count() > 0:
            return self.topics.all()[0]

        return None

    @property
    def last_poster(self):
        last_topic = self.last_topic()
        if last_topic():
            return last_topic.last_post.user.full_name

        return '-'

    def count_topics(self):
        return self.topics.count()

    def count_posts(self):
        count = 0
        for topic in self.topics.all():
            count += topic.count_posts()
        return count

    def __unicode__(self):
        return self.name


class Topic(models.Model):
    forum = models.ForeignKey(Forum, related_name='topics')
    name = models.CharField(max_length=255)
    last_post = models.ForeignKey('Post', verbose_name='Last post',
                                  related_name='forum_last_post',
                                  blank=True, null=True)

    def count_posts(self):
        return self.posts.count()

    class Meta:
        ordering = ['-last_post__created']

    def __unicode__(self):
        return self.name


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts')
    user = models.ForeignKey(ForumUser)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    indentation = models.IntegerField(default=0)
    text = RichTextField()

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.text
