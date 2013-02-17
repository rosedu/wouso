from datetime import date
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_noop, ugettext as _
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.game.models import Game

class Invitation(models.Model):
    group = models.ForeignKey('SpecialQuestGroup')
    to = models.ForeignKey('SpecialQuestUser')

    def __unicode__(self):
        return u"Invitation from %s to %s" % (self.group.head, self.to)

class GroupCompletion(models.Model):
    team = models.ForeignKey('SpecialQuestGroup')
    task = models.ForeignKey('SpecialQuestTask')

    date = models.DateTimeField(auto_now_add=True)

class SpecialQuestGroup(PlayerGroup):
    head = models.ForeignKey('SpecialQuestUser', related_name='owned_groups')
    active = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    done_tasks = models.ManyToManyField('SpecialQuestTask', blank=True, default=None, null=True,
                                        through=GroupCompletion,
                                        related_name="%(app_label)s_%(class)s_done")

    @property
    def members(self):
        return [p.get_extension(SpecialQuestUser) for p in self.players.all()]

    @property
    def completed_tasks(self):
        return GroupCompletion.objects.filter(team=self).order_by('-date')

    def is_empty(self):
        return self.players.count() < 2

    def set_task_done(self, task):
        if task not in self.done_tasks.all():
            GroupCompletion.objects.create(team=self, task=task)

    @classmethod
    def create(cls, head, name):
        game = SpecialQuestGame.get_instance()
        new_group = cls.objects.create(owner=game, name=name, head=head)
        new_group.players.add(head)
        head.group = new_group
        head.save()
        return new_group

    def __unicode__(self):
        return u"%s [%d]" % (self.name, self.players.count())

class SpecialQuestTask(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.IntegerField()

    def is_active(self, today=None):
        if today is None:
            today = date.today()
        return self.start_date <= today

    def is_archived(self, today=None):
        if today is None:
            today = date.today()
        return self.end_date < today

    @classmethod
    def active(cls):
        today = date.today()
        return cls.objects.filter(end_date__lte=today)

    @property
    def completed_teams(self):
        return GroupCompletion.objects.filter(task=self).order_by('-date')

    def __unicode__(self):
        return unicode(self.name)


class SpecialQuestUser(Player):
    group = models.ForeignKey('SpecialQuestGroup', blank=True, default=None, null=True)
    done_tasks = models.ManyToManyField(SpecialQuestTask, blank=True, default=None, null=True,
                                        related_name="%(app_label)s_%(class)s_done")

    _active_tasks = None

    @property
    def active(self):
        return self.group.active if self.group else False

    @property
    def self_group(self):
        gs = list(self.owned_groups.all())
        if not gs:
            return None
        return gs[0]

    @property
    def active_tasks(self):
        if self._active_tasks is not None:
            return self._active_tasks
        tasks = SpecialQuestTask.active()
        today = date.today()
        self._active_tasks = [t for t in tasks if t not in self.done_tasks.all() and t.start_date <= today <= t.end_date]
        return self._active_tasks

    def invitations(self):
        return self.invitation_set.all()


class SpecialQuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        # A Game extending core.game.models.Game should be set as proxy
        proxy = True

    user_model = SpecialQuestUser

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Special Quest"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "specialquest_index_view"
        super(SpecialQuestGame, self).__init__(*args, **kwargs)

    @classmethod
    def tasks_for_user(kls, user):
        """ Return a pair of tasks_done, tasks_not_done for requested user
        """
        tasks = SpecialQuestTask.objects.all()
        tasks_done = [t for t in tasks if t in user.done_tasks.all()]
        tasks_not_done = [t for t in tasks if t not in user.done_tasks.all()]
        tasks_not_done = [t for t in tasks_not_done if t.is_active()]
        return tasks_done, tasks_not_done

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return dict(text=_('Special'), link='')

    @classmethod
    def get_profile_superuser_actions(kls, request, player):
        return '<a class="button" href="%s">Special quest</a>' % reverse('specialquest_manage', args=(player.id,))

    @classmethod
    def get_formulas(kls):
        fs = []
        quest_game = kls.get_instance()
        fs.append(dict(name='specialquest-passed', definition='gold={value}',
            owner=quest_game.game,
            description='Points earned when finishing a task. Arguments: value.')
        )
        return fs

    @classmethod
    def get_profile_actions(kls, request, player):
        url = reverse('specialquest_invite', args=(player.id,))
        if request.user.get_profile().id != player.id:
            squser = request.user.get_profile().get_extension(SpecialQuestUser)
            targetuser = player.get_extension(SpecialQuestUser)
            if not squser.self_group and not targetuser.group:
                return ''
            if squser.active or targetuser.active:
                return ''
            if ((squser.self_group is not None) and (targetuser in squser.self_group.members)) or ((targetuser.group is not None) and (squser in targetuser.group.members)):
                return '<span class="button">%s</span>' % _('Special mate')
            if targetuser.group is not None:
                return '<span class="button">%s</span>' % _('Other group')
            if Invitation.objects.filter(to=targetuser, group=squser.group).count() > 0:
                return '<span class="button">%s</span>' % _('Invited')
            return '<a class="button" href="%s" title="%s">%s</a>' % (url, _("Invite in my Special Quest group"), _('Invite'))
        return ''
