from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from wouso.core.app import App
from wouso.core.user.models import Player, PlayerGroup

class ObjectHistory:
    @property
    def disabled(self):
        return Top.disabled()

class GroupHistory(ObjectHistory):
    def __init__(self, group):
        self.group = group

    @property
    def position(self):
        return History.get_group_position(self.group)

    @property
    def position_in_parent(self):
        if not self.group.parent:
            return self.position
        return History.get_group_position(self.group, relative_to=self.group.parent)

    def week_evolution(self, relative_to=None):
        """ :return: list of pairs (index, position) for the last week """
        hs = History.objects.filter(group=self.group, relative_to=relative_to).order_by('-date')[:7]
        tot = len(hs)
        return [(tot - i, h.position) for (i,h) in enumerate(hs)]

class TopUser(ObjectHistory, Player):
    @property
    def progress(self):
        """ Return position difference between last two recorded positions. """
        try:
            yesterday = History.objects.filter(user=self, relative_to=None).order_by('-date')[0]
            daybefore = History.objects.filter(user=self, relative_to=None).order_by('-date')[1]
        except Exception as e:
            return 0
        return - (yesterday.position - daybefore.position)

    @property
    def weeklyprogress(self):
        try:
            yesterday     = History.objects.filter(user=self).order_by('-date')[0]
            day1weekprior = History.objects.filter(user=self).order_by('-date')[7]
        except Exception as e:
            return 0
        return -(yesterday.position - day1weekprior.position)

    @property
    def position(self):
        return History.get_user_position(self)

    def week_evolution(self, relative_to=None):
        """ :return: list of pairs (index, position) for the last week """
        hs = History.objects.filter(user=self, relative_to=relative_to).order_by('-date')[:7]
        tot = len(hs)
        return [(tot - i, h.position) for (i,h) in enumerate(hs)]

    def week_points_evolution(self):
        """ :return: list of pairs (index, points) for the last week """
        hs = History.objects.filter(user=self, relative_to=None).order_by('-date')[:7]
        tot = len(hs)
        return [(tot - i, h.points) for (i,h) in enumerate(hs)]

class History(models.Model):
    user = models.ForeignKey('TopUser', blank=True, null=True)
    group = models.ForeignKey(PlayerGroup, blank=True, null=True)
    relative_to = models.ForeignKey(PlayerGroup, blank=True, null=True, related_name='relativeto')
    position = models.IntegerField(default=0)
    points = models.FloatField(default=0)
    date = models.DateField()

    @classmethod
    def get_user_position(kls, user, relative_to=None):
        try:
            history = History.objects.filter(user=user,relative_to=relative_to).order_by('-date')[0]
            return history.position
        except IndexError:
            return 0
        except History.DoesNotExist:
            return 0

    @classmethod
    def get_group_position(kls, group, relative_to=None):
        try:
            history = History.objects.filter(group=group, relative_to=relative_to).order_by('-date')[0]
            return history.position
        except IndexError:
            return 0
        except History.DoesNotExist:
            return 0

    def __unicode__(self):
        return u"%s %s at %s, position: %d, points: %f" % ('[%s]' % self.relative_to if self.relative_to else '',self.user if self.user else self.group, self.date, self.position, self.points)

class Top(App):

    @classmethod
    def get_sidebar_widget(kls, request):
        top5 = TopUser.objects.exclude(user__is_superuser=True).exclude(race__can_play=False)
        top5 = top5.order_by('-points')[:10]
        is_top = request.get_full_path().startswith('/top/')
        return render_to_string('top/sidebar.html',
            {'topusers': top5, 'is_top': is_top, 'top': Top}
        )

def user_post_save(sender, instance, **kwargs):
    profile = instance.get_profile()
    profile.get_extension(TopUser)
models.signals.post_save.connect(user_post_save, User)
