from ckeditor.fields import RichTextField
from django.db import models
from wouso.core.user.models import Player


class ForumUser(Player):
    def __unicode__(self):
        super(ForumUser, self).__init__()


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

    def get_latest_topic(self):
        if self.topics.count() > 0:
            return self.topics.all()[0]

        return None

    def get_latest_poster(self):
        latest_topic = self.get_latest_topic()
        if latest_topic:
            return latest_topic.last_post.user.user

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

    @property
    def first_post(self):
        return self.posts.all()[:1].get()

    def count_posts(self):
        return self.posts.count()

    class Meta:
        ordering = ['-last_post__created']

    def __unicode__(self):
        return self.name


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts')
    parent = models.ForeignKey('self', related_name='replies',
                               blank=True, null=True)
    user = models.ForeignKey(ForumUser)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    text = RichTextField()

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.text
