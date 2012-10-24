from django.db.models import Sum
import sys
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from wouso.core.app import App
from wouso.core.user.models import Player, PlayerGroup, Race
from wouso.games.challenge.models import ChallengeUser

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
    def played_challenges(self):
        return self.user.get_profile().get_extension(ChallengeUser).get_all_challenges().count()

    @property
    def won_challenges(self):
        return self.user.get_profile().get_extension(ChallengeUser).get_won_challenges().count()

    @property
    def lost_challenges(self):
        return self.user.get_profile().get_extension(ChallengeUser).get_lost_challenges().count()

    @property
    def won_perc_challenges(self):
        n = self.played_challenges
        if n == 0:
            return 0
        return float(self.won_challenges) / n * 100.0

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

class NewHistory(models.Model):
    TYPES = (('u', 'user'), ('r', 'race'), ('g', 'group'))

    object = models.IntegerField(help_text='Object id, user, race, group')
    object_type = models.CharField(max_length=1, choices=TYPES, default='u')
    relative_to = models.IntegerField(help_text='Relative to id, race or group')
    relative_to_type = models.CharField(max_length=1, choices=TYPES, default=None, blank=True, null=True)

    position = models.IntegerField(default=0)
    points = models.FloatField(default=0)
    date = models.DateField()

    @classmethod
    def record(cls, obj, date, relative_to=None):
        return cls.objects.get_or_create(object=obj.id, object_type=cls._get_type(obj), date=date,
                                  relative_to=relative_to.id, relative_to_type=cls._get_type(relative_to))[0]

    @classmethod
    def get_obj_position(cls, obj, relative_to=None):
        """
         Return the latest position computed for this object (user, race, group)
        """
        history = cls.objects.filter(object=obj.id, object_type=cls._get_type(obj),
                                     relative_to=relative_to.id, relative_to_type=cls._get_type(relative_to))
        if not history.count():
            return 0
        return history[0].position

    @classmethod
    def get_children_top(cls, obj, type):
        date = datetime.today().date()
        return type.objects.filter(id__in=cls.objects.filter(object_type=cls._get_type(type), date=date, relative_to=obj.id,
                                                      relative_to_type=cls._get_type(obj)).order_by('position').values_list('object')
        )

    @classmethod
    def get_user_position(cls, player, relative_to=None):
        """
         Return the latest position computed for this user
        """
        return cls.get_obj_position(player, relative_to)

    @classmethod
    def get_group_position(cls, group, relative_to=None):
        """
        Return the latest position of this group
        """
        return cls.get_obj_position(group, relative_to)

    @classmethod
    def _get_type(cls, object):
        if isinstance(object, Player) or isinstance(object, TopUser) or object in (Player, TopUser):
            return 'u'
        if isinstance(object, Race) or object is Race:
            return 'r'
        if isinstance(object, PlayerGroup) or object is PlayerGroup:
            return 'g'
        return None


class History(models.Model): # TODO: deprecate
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

    @classmethod
    def management_task(cls, now=None, stdout=sys.stdout):
        now = now if now is not None else datetime.now()
        today = now.date()

        # Global ladder
        stdout.write(' Updating players...\n')
        for i,u in enumerate(Player.objects.all().order_by('-points')):
            topuser = u.get_extension(TopUser)
            position = i + 1
            hs, new = History.objects.get_or_create(user=topuser, date=today, relative_to=None)
            hs.position, hs.points = position, u.points
            hs.save()

        stdout.write(' Updating group history...\n')
        for p in PlayerGroup.objects.filter(owner=None):
            p.points = p.live_points
            p.save()

        for r in Race.objects.all():
            for i, g in enumerate(r.children.annotate(lpoints=Sum('players__points')).order_by('-lpoints')):
                hs = NewHistory.record(g, today, relative_to=r)
                hs.position, hs.points = i + 1, g.points
                hs.save()

        # I don't think these are necessary, so I'm disabling them for now
        return
        # In group ladder
        for pg in PlayerGroup.objects.filter(owner=None):
            for i, u in enumerate(pg.players.all().order_by('-points')):
                topuser = u.get_extension(TopUser)
                hs, new = History.objects.get_or_create(user=topuser, date=today, relative_to=pg)
                hs.position, hs.points = i + 1, u.points
                hs.save()

        # In race ladder
        for pr in Race.objects.all():
            for i, u in enumerate(pr.player_set.all().order_by('-points')):
                hs = NewHistory.record(u, today, relative_to=pr)
                hs.position, hs.points = i + 1, u.points
                hs.save()


def user_post_save(sender, instance, **kwargs):
    profile = instance.get_profile()
    profile.get_extension(TopUser)
models.signals.post_save.connect(user_post_save, User)
