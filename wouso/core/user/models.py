# coding=utf-8
import logging
from md5 import md5
from datetime import datetime, timedelta
from random import shuffle
from django.db import models
from django.db.models import Sum, Q
from django.contrib.auth.models import User, Permission
from django.conf import settings
from wouso.core.decorators import cached_method, drop_cache
from wouso.core.game.models import Game
from wouso.core.magic.manager import MagicManager
from wouso.core.god import God
from wouso.core.magic.models import Spell
from .. import deprecated


class Race(models.Model):
    """ Groups a large set of players together and it's used extensively for 'can_play' checks.
    """
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default='', blank=True)

    artifacts = models.ManyToManyField('magic.Artifact', blank=True, through='magic.RaceArtifactAmount')

    can_play = models.BooleanField(default=True, blank=True)

    logo = models.ImageField(upload_to=settings.MEDIA_ARTIFACTS_DIR, null=True, blank=True)

    @property
    def points(self):
        """ Sum of race members points
        """
        return self.player_set.aggregate(points=Sum('points'))['points'] or 0

    @property
    def children(self):
        return self.playergroup_set.all()

    @property
    def sisters(self):
        return Race.objects.filter(can_play=self.can_play).exclude(pk=self.pk)

    def __unicode__(self):
        return self.name if not self.title else self.title


class PlayerGroup(models.Model):
    """ Group players together """
    # The group owner. If null, it belongs to the core game.
    owner = models.ForeignKey(Game, blank=True, null=True)

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default='', blank=True)
    parent = models.ForeignKey('Race', default=None, null=True, blank=True)

    artifacts = models.ManyToManyField('magic.Artifact', blank=True, through='magic.GroupArtifactAmount')
    players = models.ManyToManyField('user.Player', blank=True)

    # used only for sorting and position
    points = models.FloatField(default=0, editable=False)

    @property
    def live_points(self):
        """ Calculate sum of user points dynamically """
        p = self.players.aggregate(total=models.Sum('points'))
        if p['total'] is not None:
            return int(p['total'])
        else:
            return 0

    @property
    @deprecated('Please get rid of me')
    def children(self):
        """ All groups with parent set to this group, cached """
        return []

    @property
    @deprecated('Please get rid of me')
    def sisters(self):
        """ All groups with the same parent as this group or of the same
        class, if parent is not set.
        """
        if self.parent:
            return list(self.parent.children.exclude(id=self.id))
        else:
            return []

    @property
    def online_players(self):
        oldest = datetime.now() - timedelta(minutes=10)

        res = self.players.filter(last_seen__gte=oldest)
        return res

    def destroy(self):
        """
        Delete the group and free its members
        """
        for p in self.members:
            p.group = None
            p.save()
        self.delete()

    def __unicode__(self):
        return self.name if self.title == '' else self.title


class Player(models.Model):
    """ Base class for the game user. This is extended by game specific
    player models.
    """
    user = models.ForeignKey(User, unique=True, related_name="%(class)s_related")

    full_name = models.CharField(max_length=200)
    # Unique differentiator for ladder
    # Do not modify it manually, use scoring.score instead
    points = models.FloatField(default=0, blank=True, null=True, editable=False)

    level_no = models.IntegerField(default=1, blank=True, null=True)

    # The maximum reached level by the user
    max_level = models.IntegerField(default=0, blank=False, null=False)

    last_seen = models.DateTimeField(null=True, blank=True)

    # artifacts available for using
    artifacts = models.ManyToManyField('magic.Artifact', blank=True, through='magic.PlayerArtifactAmount')
    # spells available for casting
    spells_collection = models.ManyToManyField(Spell, blank=True, through='magic.PlayerSpellAmount', related_name='spell_collection')
    nickname = models.CharField(max_length=20, null=True, blank=False, default="admin")
    # race
    race = models.ForeignKey(Race, blank=False, default=None, null=True)
    description = models.TextField(max_length=600, blank=True)

    EXTENSIONS = {}

    def get_neighbours_from_top(self, count, user_race=None, spell_type=None):
        """ Returns an array of neighbouring players from top: count up and count down
            user_race and spell_type are used by mass spells for neighbours list.
        """
        base_query = Player.objects.exclude(user__is_superuser=True).exclude(race__can_play=False)

        allUsers = list(base_query.order_by('-points'))
        try:
            pos = allUsers.index(self)
        except ValueError:
            return []

        if (spell_type is not None) and (user_race is not None) and (spell_type != 'o'):
            if spell_type == 'p':
                allUsers = [user for user in allUsers if user.race.name == user_race.name]
            else:
                allUsers = [user for user in allUsers if user.race.name != user_race.name]

        if len(allUsers) <= 2*count+1:
            return allUsers

        start = max(pos-count, 0)
        if pos + count >= len(allUsers):
            start = len(allUsers)-2*count-1

        players = allUsers[start:start+2*count+1]
        return players

    def get_division(self, count):
        from wouso.interface.top.models import TopUser
        all_users = list(TopUser.objects.all())

        try:
            curr_user = TopUser.objects.get(id=self.id)
        except Exception:
            return []

        curr_user_pos = curr_user.position

        division = [user for user in all_users if abs(curr_user.position - user.position) < 20]
        shuffle(division)

        return division

    def user_name(self):
        return self.user.username

    def in_staff_group(self):
        return self.user.has_perm('config.change_setting')

    @property
    def race_name(self):
        return self.race.name if self.race else ''

    # Magic manager
    @property
    def magic(self):
        return MagicManager(self)

    # Other stuff
    @property
    def level(self):
        """ Return an artifact object for the current level_no.
        Ask God about the right artifact object, given the player instance.
        In the future, God may check players race and give specific artifacts.
        """
        return God.get_user_level(self.level_no, player=self)

    @property
    def coins(self):
        # TODO check usage and deprecate this function
        from wouso.core.scoring.models import History
        return History.user_coins(self.user)

    @property
    def group(self):
        return self._group()

    @cached_method
    def _group(self):
        """ Return the core game group, if any
        """
        try:
            group = self.playergroup_set.filter(owner=None).get()
        except (PlayerGroup.DoesNotExist, PlayerGroup.MultipleObjectsReturned):
            group = None
        return group

    def set_group(self, group):
        """
         Set the core group, which is unique
        """
        for g in self.playergroup_set.filter(owner=None):
            g.players.remove(self)

        group.players.add(self)
        drop_cache(self._group, self)
        return group

    def level_progress(self):
        """ Return a dictionary with: points_gained, points_left, next_level """
        return God.get_level_progress(self)

    @property
    def avatar(self):
        return self._avatar()

    @cached_method
    def _avatar(self):
        avatar = "http://www.gravatar.com/avatar/%s.jpg?d=%s" % (md5(self.user.email).hexdigest(), settings.AVATAR_DEFAULT)
        return avatar

    # special:
    #@cached_method
    def get_extension(self, cls):
        if self.__class__ is cls:
            return self
        if cls == Player:
            return self.user.get_profile()
        if self.__class__ != Player:
            obj = self.user.get_profile()
        else:
            obj = self
        return obj._get_extension(cls)

    def _get_extension(self, cls):
        """ Search for an extension of this object, with the type cls
        Create instance if there isn't any.

        Using an workaround, while: http://code.djangoproject.com/ticket/7623 gets fixed.
        Also see: http://code.djangoproject.com/ticket/11618
        """
        try:
            extension = cls.objects.get(user=self.user)
        except cls.DoesNotExist:
            extension = cls(player_ptr=self)
            for f in self._meta.local_fields:
                setattr(extension, f.name, getattr(self, f.name))
            extension.save()
        return extension

    @classmethod
    def register_extension(cls, attr, ext_cls):
        """
        Register new attribute with an ext_cls
        """
        cls.EXTENSIONS[attr] = ext_cls

    @classmethod
    def get_quest_gods(cls):
        from wouso.core.scoring.models import History
        from wouso.games.quest.models import QuestGame, QuestResult

        def quest_points(user):
            return int(History.objects.filter(game=QuestGame.get_instance(),
                                              user=user).aggregate(points=Sum('amount'))['points'] or 0)

        users = list(cls.objects.exclude(race__can_play=False).filter(
            id__in=QuestResult.objects.values_list('user')))
        users.sort(lambda b, a: quest_points(a) - quest_points(b))
        gods = users[:10]
        return gods

    @classmethod
    def get_by_permission(cls, permission):
        perm = Permission.objects.get(codename=permission)
        users = User.objects.filter(Q(groups__permissions=perm) |
                                    Q(user_permissions=perm)).distinct()
        return Player.objects.filter(user__in=users)

    @property
    def race_name(self):
        return self._race_name()

    @cached_method
    def _race_name(self):
        if self.race:
            return self.race.name
        return ''

    def save(self, **kwargs):
        """ Clear cache for extensions
        """
        #for k, v in self.EXTENSIONS.iteritems():
        #    drop_cache(self.get_extension, self, v)
        #drop_cache(self.get_extension, self, self.__class__)
        drop_cache(self._race_name, self)
        drop_cache(self._group, self)
        update_display_name(self, save=False)
        return super(Player, self).save(**kwargs)

    def __getitem__(self, item):
        if item in self.__class__.EXTENSIONS:
            return self.get_extension(self.__class__.EXTENSIONS[item])
        return super(Player, self).__getitem__(item)

    def __unicode__(self):
        return self.full_name or self.user.__unicode__()


# Hack for having user and user's profile always in sync
def user_post_save(sender, instance, **kwargs):
    profile, new = Player.objects.get_or_create(user=instance)
    if new:
        # add in default group
        from wouso.core.config.models import ChoicesSetting
        try:
            default_group = PlayerGroup.objects.get(pk=int(ChoicesSetting.get('default_group').get_value()))
        except (PlayerGroup.DoesNotExist, ValueError):
            pass
        else:
            default_group.players.add(profile)

        try:
            default_race = Race.objects.get(pk=int(ChoicesSetting.get('default_race').get_value()))
        except (Race.DoesNotExist, ValueError):
            pass
        else:
            profile.race = default_race
            profile.save()
        profile.nickname = profile.user.username
        profile.save()
    update_display_name(profile)

models.signals.post_save.connect(user_post_save, User)


def update_display_name(player, save=True):
    display_name = unicode(settings.DISPLAY_NAME).format(first_name=player.user.first_name,
                                                         last_name=player.user.last_name,
                                                         nickname=player.nickname).strip()
    player.full_name = display_name
    if save:
        player.save()
