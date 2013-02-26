from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from wouso.core.game import Game
from wouso.core.qpool import register_category
from wouso.core.qpool.models import Question, Category
from wouso.core.user.models import Player
from wouso.games.challenge.models import Challenge, ChallengeManager

(STATUS_NEW,
 STATUS_PROPOSED,
 STATUS_REJECTED,
 STATUS_ACTIVE,
 STATUS_PLAYABLE,
 STATUS_DONE) = range(6)

class SpecialChallenge(models.Model):
    STATUSES = (
        (STATUS_NEW, _('New, editing')),
        (STATUS_PROPOSED, _('Proposed for review')),
        (STATUS_REJECTED, _('Rejected by reviewer')),
        (STATUS_ACTIVE, _('Reviewed, active')),
        (STATUS_PLAYABLE, _('Playable')),
        (STATUS_DONE, _('Played, done')),
    )
    player_from = models.ForeignKey(Player, related_name='specialchallenges_from')
    player_to = models.ForeignKey(Player, related_name='specialchallenges_to')
    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_NEW)
    questions = models.ManyToManyField(Question, blank=True, default=None)
    amount = models.IntegerField(default=0, help_text='Amount of points earned/lost after this challenge')
    real_challenge = models.OneToOneField(Challenge, null=True, blank=True)

    @classmethod
    def create(cls, player_from, player_to):
        return cls.objects.create(player_from=player_from, player_to=player_to)

    def launch(self):
        if self.is_editable():
            self.status = STATUS_PROPOSED
            self.save()
            return True
        return False

    def set_active(self):
        if not self.is_editable():
            self.status = STATUS_ACTIVE
            self.save()

    def is_editable(self):
        return self.status in (STATUS_NEW, STATUS_REJECTED)

    def is_active(self):
        return self.status == STATUS_ACTIVE

    def is_played(self):
        return self.status == STATUS_DONE

    def update_challenge(self):
        """
        Create real challenge if status is Active
        """
        if self.is_active():
            if self.real_challenge:
                return
            self.real_challenge = Challenge.create_custom(self.player_from, self.player_to, self.questions.all(), SpecialChallengeGame.get_instance())
            self.save()
            if self.real_challenge:
                self.status = STATUS_PLAYABLE
                self.save()


    def __unicode__(self):
        return u"#%d against %s" % (self.id, self.player_to)


class SpecialChallengeManager(ChallengeManager):
    def accept(self):
        self.challenge.user_from.played = True
        self.challenge.user_from.save()

    def get_result(self):
        if self.challenge.user_to.score > self.challenge.user_from.score:
            result = (self.challenge.user_to, self.challenge.user_from)
        elif self.challenge.user_from.score > self.challenge.user_to.score:
            result = (self.challenge.user_from, self.challenge.user_to)
        else: #draw game
            result = 'draw'
        return result

    def score(self):
        special_challenge = SpecialChallenge.objects.get(real_challenge=self.challenge)
        special_challenge.status = STATUS_DONE
        special_challenge.save()


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
        if kls.disabled():
            return ''
        return render_to_string('specialchallenge/sidebar.html', {})

    @classmethod
    def get_manager(cls, challenge):
        return SpecialChallengeManager(challenge)

register_category(SpecialChallengeGame.QPOOL_CATEGORY, SpecialChallengeGame)