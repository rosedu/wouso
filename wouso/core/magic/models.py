import sys
import os.path
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
from wouso.core.app import App

class Modifier(models.Model):
    """ Basic model for all the magic.
    It is extended by:
        - Artifact (adding image, groupping and percents)
        - Spell (all of artifact + time cast)
    """
    class Meta:
        abstract = True

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100) # Maturator
    image = models.ImageField(upload_to=settings.MEDIA_ARTIFACTS_DIR, blank=True, null=True)

    percents = models.IntegerField(default=100)

    @property
    def path(self):
        """ Image can be stored inside uploads or in theme, return the
        full path or the css class. """
        if self.image:
            return "%s/%s" % (settings.MEDIA_ARTIFACTS_URL, os.path.basename(str(self.image)))

        if hasattr(self, 'group'):
            return ("%s-%s" %  (self.group, self.name)).lower()

        return self.name.lower()


class ArtifactGroup(models.Model):
    """ A group of artifacts for a Species. It cannot contain two artifacts of the same name."""
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

class Artifact(Modifier):
    """ The generic artifact model. This should contain the name (identifier) and group,
    but also personalization such as: image (icon) and title
    """
    class Meta:
        unique_together = ('name', 'group', 'percents')

    group = models.ForeignKey(ArtifactGroup)

    @classmethod
    def DEFAULT(kls):
        # TODO: get rid of me
        return ArtifactGroup.objects.get_or_create(name='Default')[0]

    def __unicode__(self):
        return u"%s [%s]" % (self.name, self.group.name)


class NoArtifactLevel(object):
    """
    Mock an artifact object
    """
    def __init__(self, level_no):
        self.id = ''
        self.name = 'level-%s' % level_no
        self.title = 'Level %s' % level_no
        self.image = ''
        self.path = 'default-%s' % self.name
        self.group = None


class Spell(Modifier):
    TYPES = (('o', 'neutral'), ('p', 'positive'), ('n', 'negative'), ('s', 'self'))

    description = models.TextField() # Extended description shown in the magic place
    type = models.CharField(max_length=1, choices=TYPES, default='o')
    due_days = models.IntegerField(default=5) # How many days may the spell be active
    mass = models.BooleanField(default=False) # Apply spell on many players at once

    price = models.FloatField(default=10)       # Spell price in gold.
    level_required = models.IntegerField(default=0) # Level required for buying this spell
    available = models.BooleanField(default=True)   # Spell can be bought in Bazaar

    @property
    def group(self):
        return 'spells'

    def history_bought(self):
        return self.spellhistory_set.filter(type='b').count()

    def history_used(self):
        return self.spellhistory_set.filter(type='u').count()

    def history_cleaned(self):
        return self.spellhistory_set.filter(type='c').count()

    def history_expired(self):
        return self.spellhistory_set.filter(type='e').count()


    def __unicode__(self):
        return u'spell %s' % self.name


class SpellHistory(models.Model):
    TYPES = (('b', 'bought'), ('u', 'used'), ('c', 'cleaned'), ('e', 'expired'))

    type = models.CharField(max_length=1, choices=TYPES)
    user_from = models.ForeignKey('user.Player', related_name='sh_from')
    user_to = models.ForeignKey('user.Player', blank=True, null=True, default=None, related_name='sh_to')
    date = models.DateTimeField(auto_now_add=True)
    spell = models.ForeignKey(Spell)

    @classmethod
    def log(cls, type, user, spell, user_to=None):
        cls.objects.create(user_from=user, spell=spell, user_to=user_to, type=type)

    @classmethod
    def bought(cls, user, spell):
        cls.log('b', user, spell)

    @classmethod
    def expired(cls, user, spell):
        cls.log('e', user, spell)

    @classmethod
    def used(cls, user, spell, dest):
        if spell.name == 'dispell':
            type = 'c'
        else:
            type = 'u'
        cls.log(type, user, spell, user_to=dest)

    def __unicode__(self):
        if self.type == 'b':
            return u"%s bought %s" % (self.user_from, self.spell)
        if self.type == 'c':
            return u"%s cleared %s" % (self.user_from, self.user_to)
        if self.type == 'u':
            return u"%s cast %s on %s" % (self.user_from, self.spell, self.user_to)
        if self.type == 'e':
            return u"%s expired %s" % (self.user_from, self.spell)
        return "%s %s %s" % (self.type, self.user_from, self.spell)


# Tolbe

class RaceArtifactAmount(models.Model):
    class Meta:
        unique_together = ('race', 'artifact')

    race = models.ForeignKey('user.Race')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)


class GroupArtifactAmount(models.Model):
    """ Tie artifact and amount to the owner group """
    class Meta:
        unique_together = ('group', 'artifact')
    group = models.ForeignKey('user.PlayerGroup')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)


class PlayerArtifactAmount(models.Model):
    """ Tie artifact and amount to the owner user """
    class Meta:
        unique_together = ('player', 'artifact')
    player = models.ForeignKey('user.Player')
    artifact = models.ForeignKey(Artifact)
    amount = models.IntegerField(default=1)

    def __unicode__(self):
        return u"%s has %s [%d]" % (self.player, self.artifact, self.amount)


class PlayerSpellAmount(models.Model):
    """ Tie spells to collecting user """
    class Meta:
        unique_together = ('player', 'spell')
    player = models.ForeignKey('user.Player')
    spell = models.ForeignKey(Spell)
    amount = models.IntegerField(default=1)

    def __unicode__(self):
        return u"%s has %s [%d]" % (self.player, self.spell, self.amount)


class PlayerSpellDue(models.Model):
    """ Tie spell, casting user, duration with the victim player """
    class Meta:
        unique_together = ('player', 'spell')
    player = models.ForeignKey('user.Player')
    spell = models.ForeignKey(Spell)
    source = models.ForeignKey('user.Player', related_name='spell_source')
    due = models.DateTimeField()

    seen = models.BooleanField(default=False, blank=True) # if the target have seen it

    @staticmethod
    def get_expired(date):
        return PlayerSpellDue.objects.filter(due__lte=date)

    def __unicode__(self):
        return u"%s casted on %s until %s [%s]" % (self.spell, self.player, self.due, self.source)


class Bazaar(App):
    @classmethod
    def get_header_link(kls, request):
        url = reverse('bazaar_home')
        player = request.user.get_profile() if request.user.is_authenticated() else None
        if player:
            count = PlayerSpellDue.objects.filter(player=player, seen=False).count()
        else:
            count = 0

        return dict(link=url, text=_('Magic'), count=count)

    @classmethod
    def management_task(cls, datetime=lambda: datetime.now(), stdout=sys.stdout):
        spells = PlayerSpellDue.get_expired(datetime)

        stdout.write(" %d expired spells\n" % spells.count())
        for s in spells:
            SpellHistory.expired(s.player, s.spell)
            s.delete()
