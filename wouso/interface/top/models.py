from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from wouso.core.app import App
from wouso.core.user.models import Player, PlayerGroup
from wouso.interface import render_string

class GroupHistory:
    def __init__(self, group):
        self.group = group

    @property
    def position(self):
        return History.get_group_position(self.group)

    def week_evolution(self):
        """ :return: list of pairs (index, position) for the last week """
        hs = History.objects.filter(group=self.group).order_by('-date')[:7]
        return [(i + 1, h.position) for (i,h) in enumerate(hs)]

class TopUser(Player):
    @property
    def progress(self):
        try:
            yesterday = History.objects.filter(user=self).order_by('-date')[0]
            daybefore = History.objects.filter(user=self).order_by('-date')[1]
        except Exception as e:
            return 0
        return yesterday.position - daybefore.position

    @property
    def weeklyprogress(self):
        try:
            yesterday     = History.objects.filter(user=self).order_by('-date')[0]
            day1weekprior = History.objects.filter(user=self).order_by('-date')[7]
        except Exception as e:
            return 0
        return yesterday.position - day1weekprior.position

    @property
    def position(self):
        return History.get_user_position(self)

    def week_evolution(self):
        """ :return: list of pairs (index, position) for the last week """
        hs = History.objects.filter(user=self).order_by('-date')[:7]
        return [(i + 1, h.position) for (i,h) in enumerate(hs)]

class History(models.Model):
    user = models.ForeignKey('TopUser', blank=True, null=True)
    group = models.ForeignKey(PlayerGroup, blank=True, null=True)
    position = models.IntegerField(default=0)
    points = models.FloatField(default=0)
    date = models.DateField()

    @classmethod
    def get_user_position(kls, user):
        try:
            history = History.objects.filter(user=user).order_by('-date')[0]
            return history.position
        except IndexError:
            return 0
        except History.DoesNotExist:
            return 0

    @classmethod
    def get_group_position(kls, group):
        try:
            history = History.objects.filter(group=group).order_by('-date')[0]
            return history.position
        except IndexError:
            return 0
        except History.DoesNotExist:
            return 0

    def __unicode__(self):
        return u"%s at %s, position: %d, points: %f" % (self.user if self.user else self.group, self.date, self.position, self.points)

class Top(App):

    @classmethod
    def get_sidebar_widget(kls, request):
        top5 = TopUser.objects.all().order_by('-points')[:5]
        is_top = request.get_full_path().startswith('/top/')
        return render_string('top/sidebar.html',
            {'topusers': top5, 'is_top': is_top}
        )

def user_post_save(sender, instance, **kwargs):
    profile = instance.get_profile()
    profile.get_extension(TopUser)
models.signals.post_save.connect(user_post_save, User)
