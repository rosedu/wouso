from django.db import models
from django.contrib.auth.models import User, Group
from wouso.core.scoring.models import History
from wouso.core.artifacts.models import Artifact

class PlayerGroup(models.Model):
    group = models.ForeignKey(Group, unique=True, related_name="%(class)s_related")
    name = models.CharField(max_length=100)
    gclass = models.IntegerField(default=0)
    parent = models.ForeignKey('PlayerGroup', default=None, null=True, blank=True)
    points = models.FloatField(default=0)

    @property
    def live_points(self):
        p = self.userprofile_set.aggregate(total=models.Sum('points'))
        if p['total'] is None:
            return 0
        return p['total']

    @property
    def children(self):
        return self.playergroup_set.all()

    def __unicode__(self):
        return self.name

class Player(models.Model):
    user = models.ForeignKey(User, unique=True,
        related_name="%(class)s_related")

    # Unique differentiator for ladder
    # Do not modify it manually, use scoring.score instead
    points = models.FloatField(default=0, blank=True, null=True)

    level_no = models.IntegerField(default=1, blank=True, null=True)
    level = models.ForeignKey(Artifact, default=Artifact.get_level_1, related_name='user_level', blank=True, null=True)

    last_seen = models.DateTimeField(null=True, blank=True)

    artifacts = models.ManyToManyField(Artifact, blank=True)
    groups = models.ManyToManyField(PlayerGroup, blank=True)

    @property
    def coins(self):
        return History.user_coins(self.user)

    @property
    def proximate_group(self):
        res = self.groups.aggregate(gclass=models.Min('gclass'))
        if res['gclass'] is None:
            return None

        return self.groups.filter(gclass=res['gclass'])[0]

    def get_extension(self, cls):
        """ Search for an extension of this object, with the type cls
        Create instance if there isn't any.

        Using an workaround, while: http://code.djangoproject.com/ticket/7623 gets fixed.
        Also see: http://code.djangoproject.com/ticket/11618
        """
        try:
            extension = cls.objects.get(user=self.user)
        except cls.DoesNotExist:
            extension = cls(player_ptr = self)
            for f in self._meta.local_fields:
                setattr(extension, f.name, getattr(self, f.name))
            extension.save()

        return extension

    def __unicode__(self):
        return u"%s %s" % (self.user.first_name, self.user.last_name)

# Hack for having user and user's profile always in sync
def user_post_save(sender, instance, **kwargs):
    profile, new = Player.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, User)
