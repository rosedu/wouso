from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from wouso.core.game import Game
from wouso.core.qpool import register_category
from wouso.core.qpool.models import Question, Category
from wouso.core.user.models import Player

(STATUS_NEW,
 STATUS_PROPOSED,
 STATUS_REJECTED,
 STATUS_ACTIVE,
 STATUS_DONE) = range(5)

class SpecialChallenge(models.Model):
    STATUSES = (
        (STATUS_NEW, _('New, editing')),
        (STATUS_PROPOSED, _('Proposed for review')),
        (STATUS_REJECTED, _('Rejected by reviewer')),
        (STATUS_ACTIVE, _('Reviewed, active')),
        (STATUS_DONE, _('Played, done')),
    )
    player_from = models.ForeignKey(Player, related_name='specialchallenges_from')
    player_to = models.ForeignKey(Player, related_name='specialchallenges_to')
    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_NEW)
    questions = models.ManyToManyField(Question, blank=True, default=None)
    amount = models.IntegerField(default=0, help_text='Amount of points earned/lost after this challenge')

    @classmethod
    def create(cls, player_from, player_to):
        return cls.objects.create(player_from=player_from, player_to=player_to)

    def __unicode__(self):
        return u"#%d against %s" % (self.id, self.player_to)


class SpecialChallengeGame(Game):
    class Meta:
        proxy = True
    QPOOL_CATEGORY = 'specialchallenge'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Special Challenge"
        self._meta.get_field('short_name').default = ""
        self._meta.get_field('url').default = "specialchallenge_index"
        super(SpecialChallengeGame, self).__init__(*args, **kwargs)

    @classmethod
    def get_category(cls):
        return Category.objects.get(name=cls.QPOOL_CATEGORY)

    @classmethod
    def get_sidebar_widget(kls, request):
        return render_to_string('specialchallenge/sidebar.html', {})

register_category(SpecialChallengeGame.QPOOL_CATEGORY, SpecialChallengeGame)