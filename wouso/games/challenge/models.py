import logging
from datetime import datetime, time, timedelta, date
from random import shuffle
import pickle as pk
from django.db import models
from django.db.models import Q, Max
from django.utils.translation import ugettext_noop, ugettext as _
from django.core.urlresolvers import reverse
from wouso.core.user.models import Player
from wouso.core.magic.manager import InsufficientAmount
from wouso.core.qpool.models import Question
from wouso.core.qpool import get_questions_with_category
from wouso.core.game.models import Game
from wouso.core import scoring
from wouso.core.god import God
from wouso.interface.activity import signals


class ChallengeException(Exception):
    pass

class ChallengeUser(Player):
    """ Extension of the userprofile, customized for challenge """

    last_launched = models.DateTimeField(default=datetime(1, 1, 1), blank=True, null=True)

    def is_eligible(self):
        return God.user_is_eligible(self, ChallengeGame)

    def can_launch(self):
        """ Check if 1 challenge per day restriction apply
        """
        now = datetime.now()
        today_start = datetime.combine(now, time())
        today_end = datetime.combine(now, time(23, 59, 59))
        if today_start <= self.last_launched <= today_end:
            return False
        if self.has_modifier('challenge-cannot-challenge'):
            return False
        return True

    def has_enough_points(self):
        """ Check if the user has 30 points to challenge
        """
        REQ_POINTS = 30
        return self.points >= REQ_POINTS

    def can_challenge(self, user):
        """ Check if the target user is available.
        """
        user = user.get_extension(ChallengeUser)
        if self.user == user.user:
            # Cannot challenge myself
            return False
        if user.has_modifier('challenge-cannot-be-challenged'):
            return False
        return God.user_can_interact_with(self, user, game=ChallengeGame)

    def has_one_more(self):
        return self.has_modifier('challenge-one-more')

    def do_one_more(self):
        try:
            modifier = self.use_modifier('challenge-one-more', 1)
        except InsufficientAmount:
            return False
        self.last_launched -= timedelta(days=-1)
        self.save()

        signal_msg = ugettext_noop('used {artifact} to enable one more challenge.')
        signals.addActivity.send(sender=None, user_from=self, \
                                     user_to=self, \
                                     message=signal_msg, \
                                     arguments=dict(artifact=modifier.artifact.title), \
                                     game=ChallengeGame.get_instance())
        return True

    def can_play(self, challenge):
        return challenge.can_play(self)

    def launch_against(self, destination):
        destination = destination.get_extension(ChallengeUser)

        if destination.id == self.id:
            raise ChallengeException('Cannot launch against myself')

        if not self.can_launch():
            raise ChallengeException('Player cannot launch')

        if not self.can_challenge(destination):
            raise ChallengeException('Player cannot launch against this opponent')

        return Challenge.create(user_from=self, user_to=destination)

class Participant(models.Model):
    user = models.ForeignKey(ChallengeUser)
    start = models.DateTimeField(null=True, blank=True)
    seconds_took = models.IntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    responses = models.TextField(default='', blank=True, null=True)
    #score = models.FloatField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    @property
    def challenge(self):
        try:
            return Challenge.objects.get(Q(user_from=self)|Q(user_to=self))
        except Challenge.DoesNotExist:
            return None

    def __unicode__(self):
        return unicode(self.user)

class Challenge(models.Model):
    STATUS = (
        ('L', 'Launched'),
        ('A', 'Accepted'),
        ('R', 'Refused'),
        ('P', 'Played'),
        ('D', 'Draw'),
    )
    user_from = models.ForeignKey(Participant, related_name="user_from")
    user_to = models.ForeignKey(Participant, related_name="user_to")
    date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='L')
    winner = models.ForeignKey(ChallengeUser, related_name="winner", null=True, blank=True)
    questions = models.ManyToManyField(Question)
    nr_q = 0
    LIMIT = 5
    TIME_LIMIT = 300 # seconds
    TIME_SAFE = 10 # seconds more

    @staticmethod
    def create(user_from, user_to, ignore_questions = False):
        """ Assigns questions, and returns the number of assigned q """

        questions = [q for q in get_questions_with_category('challenge')]
        if (len(questions) < 5) and not ignore_questions:
            raise ChallengeException('Too few questions')
        shuffle(questions)

        uf, ut = Participant(user=user_from), Participant(user=user_to)
        uf.save(), ut.save()

        c = Challenge(user_from=uf, user_to=ut, date=datetime.now())
        c.save()

        # TODO: better question selection
        #limit = 5
        for q in questions[:Challenge.LIMIT]:
            c.questions.add(q)

        # set last_launched
        user_from.last_launched = datetime.now()
        user_from.save()

        # take 3 points from user_from
        scoring.score(user_from, ChallengeGame, 'chall-warranty', external_id=c.id)
        return c

    @staticmethod
    def get_expired(today):
        """
        Return all expired candidate challenges at given date.
        """
        yesterday = today + timedelta(days=-1)
        return Challenge.objects.filter(date__lt=yesterday).filter(Q(status='A')|Q(status='L'))

    @classmethod
    def exist_last_day(cls, today, user_from, user_to):
        """
        Return true if there are any challenges between the two users in the last day
        """
        yesterday = today + timedelta(days=-1)
        return Challenge.objects.filter(user_from__user=user_from, user_to__user=user_to, date__gt=yesterday).count() > 0

    @classmethod
    def last_between(cls, user_from, user_to):
        try:
            return Challenge.objects.filter(user_from__user=user_from, user_to__user=user_to).exclude(status='R').order_by('-date')[0]
        except IndexError:
            return None

    @property
    def participants(self):
        return (self.user_from, self.user_to)

    def participant_for_player(self, player):
        player = player.get_extension(ChallengeUser)
        if self.user_from.user == player:
            return self.user_from
        elif self.user_to.user == player:
            return self.user_to
        raise ValueError('Not participating in this challenge')

    def accept(self):
        self.status = 'A'
        self.save()
        # take warranty from user_to
        scoring.score(self.user_to.user, ChallengeGame, 'chall-warranty', external_id=self.id)

    def refuse(self, auto=False):
        self.status = 'R'
        self.user_from.user.last_launched = datetime(1, 1, 1)
        self.user_from.user.save()

        # send activity signal
        if auto:
            signal_msg = ugettext_noop('has refused challenge from {chall_from} (expired)')
        else:
            signal_msg = ugettext_noop('has refused challenge from {chall_from}')
        signals.addActivity.send(sender=None, user_from=self.user_to.user, \
                                     user_to=self.user_from.user, \
                                     message=signal_msg, \
                                     arguments=dict(chall_from=self.user_from), \
                                     game=ChallengeGame.get_instance())
        self.save()
        # give warranty back to initiator
        scoring.unset(self.user_from.user, ChallengeGame, 'chall-warranty', external_id=self.id)

    def cancel(self):
        # give warranty back to initiator
        scoring.unset(self.user_from.user, ChallengeGame, 'chall-warranty', external_id=self.id)

        self.user_from.user.last_launched = datetime(1, 1, 1)
        self.user_from.user.save()
        self.delete()

    def set_start(self, user):
        """ Update user.start and set playing time to now
        This is called when one of the participants sees the challenge for the
        first time.
        After this call, challenge will be visible to him for 5 minutes
        TODO: check it hasn't been already started in the past"""

        partic = self.participant_for_player(user)

        partic.start = datetime.now()
        partic.save()

    def set_expired(self):
        if not self.user_from.played:
            self.user_from.score = 0.0
            self.user_from.played = True

        if not self.user_to.played:
            self.user_to.score = 0.0
            self.user_to.played = True

        # send expired activity
        self.played()

    def time_for_user(self, user):
        now = datetime.now()
        partic = self.participant_for_player(user)

        return Challenge.TIME_LIMIT - (now - partic.start).seconds

    def is_expired(self, participant):
        """ This function assumes that seconds_took has been set.
        If the user didn't submit the challenge, this will return False
        which might be incorrect.
        TODO: fix this to first check if user has submitted, and
        if not, verify with datetime.now - participant.start.
        """
        if participant.start is None:
            return False
        if participant.seconds_took < Challenge.TIME_LIMIT + Challenge.TIME_SAFE:
            return False
        return True

    def is_expired_for_user(self, user):
        """ Check if the challenge has expired for the user
        """
        partic = self.participant_for_player(user)
        return self.is_expired(partic)

    def is_started_for_user(self, user):
        """ Check if the challenge has already started for the given user"""
        partic = self.participant_for_player(user)
        if partic.start is None:
            return False
        return True

    def extraInfo(self, user_won, user_lost):
        '''returns a string with extra info for a string such as User 1 finished the challenge in $SECONDS seconds
        (or $MINUTES minutes and seconds) and scored X points)'''

        def formatTime(seconds):
            if seconds is None:
                return _('expired')
            ret = ''
            if seconds < 60:
                ret = _("{seconds} seconds").format(seconds=seconds)
            elif seconds == 60:
                ret = _('1 minute')
            elif seconds % 60 == 0:
                ret = _('{minutes} minutes').format(minutes=(seconds/60))
            elif 60 < seconds < 120:
                ret = _('1 minute and {s} seconds').format(s=seconds % 60)
            else:
                ret = _('{m} minutes and {s} seconds').format(m=seconds / 60, s=seconds % 60)
            return _('(in {time})').format(time=ret)

        return '%dp %s - %dp %s' % (user_won.score, formatTime(user_won.seconds_took),
                                        user_lost.score, formatTime(user_lost.seconds_took))

    def played(self):
        """ Both players have played, save and score
        Notice the fact this is the only function where the scoring is affected
        """
        """ Handle artifacts and spells """
        for u in (self.user_to, self.user_from):
            # always lose, you mofo
            if u.user.has_modifier('challenge-always-lose'):
                u.score = -1
            # affect bonuses
            if u.user.has_modifier('challenge-affect-scoring'):
                u.percents = u.user.modifier_percents('challenge-affect-scoring')
            else:
                u.percents = 100

        if self.user_to.score > self.user_from.score:
            result = (self.user_to, self.user_from)
        elif self.user_from.score > self.user_to.score:
            result = (self.user_from, self.user_to)
        else: #draw game
            result = 'draw'

        if result == 'draw':
            self.status = 'D'
            scoring.score(self.user_to.user, ChallengeGame, 'chall-draw', percents=self.user_to.percents)
            scoring.score(self.user_from.user, ChallengeGame, 'chall-draw', percents=self.user_from.percents)
            # send activty signal
            signal_msg = ugettext_noop('draw result between {user_to} and {user_from}:\n{extra}')
            signals.addActivity.send(sender=None, user_from=self.user_to.user, \
                                     user_to=self.user_from.user, \
                                     message=signal_msg, \
                                     arguments=dict(user_to=self.user_to, user_from=self.user_from,
                                                    extra=self.extraInfo(self.user_from, self.user_to)),\
                                     game=ChallengeGame.get_instance())
        else:
            self.status = 'P'
            self.user_won, self.user_lost = result
            self.winner = self.user_won.user
            diff_race = self.user_won.user.series != self.user_lost.user.series
            diff_class = self.user_won.user.proximate_group != self.user_lost.user.proximate_group
            diff_race = 1 if diff_race else 0
            diff_class = 1 if diff_class else 0
            winner_points = self.user_won.user.points
            loser_points = self.user_lost.user.points

            # warranty not affected by percents
            scoring.score(self.user_won.user, ChallengeGame, 'chall-warranty-return',
                          external_id=self.id)

            scoring.score(self.user_won.user, ChallengeGame, 'chall-won',
                external_id=self.id, percents=self.user_won.percents,
                points=self.user_won.score, points2=self.user_lost.score,
                different_race=diff_race, different_class=diff_class,
                winner_points=winner_points, loser_points=loser_points,
            )
            scoring.score(self.user_lost.user, ChallengeGame, 'chall-lost',
                external_id=self.id, points=self.user_lost.score, points2=self.user_lost.score)
            # send activty signal
            signal_msg = ugettext_noop('won challenge with {user_lost}: {extra}')
            signals.addActivity.send(sender=None, user_from=self.user_won.user, \
                                     user_to=self.user_lost.user, \
                                     message=signal_msg, arguments=dict(user_lost=self.user_lost,
                                                                        extra=self.extraInfo(self.user_won, self.user_lost)), \
                                     game=ChallengeGame.get_instance())
        self.save()

    def _calculate_points(self, responses):
        """ Response contains a dict with question id and checked answers ids.
        Example:
            1 : [14], - has answered answer with id 14 at the question with id 1
        """
        points = 0.0
        for r, v in responses.iteritems():
            checked, missed = 0, 0
            q = Question.objects.get(id=r)
            for a in q.answers.all():
                if a.correct:
                    if a.id in v:
                        checked += 1
                    else:
                        missed += 1
                elif a.id in v:
                    missed += 1
            correct_count = len([a for a in q.answers if a.correct])
            wrong_count = len([a for a in q.answers if not a.correct])
            if correct_count == 0:
                qpoints = 1 if (len(v) == 0) else 0
            elif wrong_count == 0:
                qpoints = 1 if (len(v) == q.answers.count()) else 0
            else:
                qpoints = float(checked) / correct_count - float(missed) / wrong_count
            qpoints = qpoints if qpoints > 0 else 0
            points += qpoints
        return int(100.0 * points)

    def set_played(self, user, responses):
        """ Set user's results. If both users have played, also update self and activity. """
        user_played = self.participant_for_player(user)

        user_played.seconds_took = (datetime.now() - user_played.start).seconds
        user_played.played = True
        user_played.responses = pk.dumps(responses)
        exp = False
        if self.is_expired(user_played):
            exp = True
            user_played.score = 0.0
        else:
            user_played.score = self._calculate_points(responses)
        user_played.save()

        if self.user_to.played and self.user_from.played:
            self.played()

        if exp:
            return {'points': '0.0 (expired)'}
        return {'points': user_played.score}

    def can_play(self, user):
        """ Check if user can play this challenge"""
        try:
            partic = self.participant_for_player(user)
        except ValueError:
            return False

        if partic.played:
            return False

        return self.is_runnable()

    def is_launched(self):
        return self.status == 'L'

    def is_runnable(self):
        return self.status == 'A'

    def is_refused(self):
        return self.status == 'R'

    def __unicode__(self):
        return "%s vs %s (%s) - %s [%d] " % (
            unicode(self.user_from),
            unicode(self.user_to),
            self.date,
            self.status,
            self.questions.count())

class ChallengeGame(Game):
    """ Each game must extend Game """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Challenges"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "challenge_index_view"
        super(ChallengeGame, self).__init__(*args, **kwargs)

    @staticmethod
    def get_active(user):
        """ Return a list of active (runnable) challenges for a user """
        user = user.get_extension(ChallengeUser)
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user=user, played=False)).order_by('-id') if p.challenge.is_launched() or p.challenge.is_runnable()]
        except Participant.DoesNotExist:
            challs = []
        return challs

    @staticmethod
    def get_played(user):
        """ Return a list of played (scored TODO) challenges for a user """
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user=user, played=True)).order_by('-id')]
        except Participant.DoesNotExist:
            challs = []
        return challs

    @staticmethod
    def get_expired(user):
        """ Return a list of status != L/A challenges, where played = False """
        # TODO
        return []

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        chall_game = kls.get_instance()
        fs.append(dict(id='chall-won', formula='points=6+{different_race}+{different_class}',
            owner=chall_game.game,
            description='Points earned when winning a challenge. Arguments: different_race (int 0,1), different_class (int 0,1)')
        )
        fs.append(dict(id='chall-lost', formula='points=2',
            owner=chall_game.game,
            description='Points earned when losing a challenge')
        )
        fs.append(dict(id='chall-draw', formula='points=4',
            owner=chall_game.game,
            description='Points earned when drawing a challenge')
        )
        fs.append(dict(id='chall-warranty', formula='points=-3',
            owner=chall_game.game,
            description='Points taken as a warranty for challenge'))
        fs.append(dict(id='chall-warranty-return', formula='points=3',
            owner=chall_game.game,
            description='Points given back as a warranty taken for challenge'))
        return fs

    @classmethod
    def get_modifiers(kls):
        """
        Challenge game modifiers
        """
        return ['challenge-one-more', # challenge twice a day, positive
                'challenge-cannot-be-challenged', # reject incoming challenges, negative
                'challenge-cannot-challenge', # reject outgoing challenges, negative
                'challenge-always-lose', # lose regardless the result, negative
                'challenge-affect-scoring', # affect scoring by positive/negative percent
        ]

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return dict(text=_('Challenges'), link='')

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

    @classmethod
    def get_profile_actions(kls, request, player):
        url = reverse('wouso.games.challenge.views.launch', args=(player.id,))
        if request.user.get_profile().id != player.id:
            # check if there isn't another challenge launched
            if Challenge.exist_last_day(date.today(), request.user.get_profile(), player):
                return '<span class="button">%s</span>' % _('Challenged')
            return '<a class="button ajaxify" href="%s">%s</a>' % (url, _('Challenge!'))
        return ''

    @classmethod
    def get_profile_superuser_actions(kls, request, player):
        url = reverse('wouso.games.challenge.views.history', args=(player.id,))
        return '<a class="button" href="%s">%s</a>' % (url, _('Challenges'))

    @classmethod
    def get_api(kls):
        from piston.handler import BaseHandler
        from piston.utils import rc
        class ChallengesHandler(BaseHandler):
            methods_allowed = ('GET',)
            def read(self, request):
                player = request.user.get_profile()
                challuser = player.get_extension(ChallengeUser)
                return [dict(status=c.status, date=c.date, id=c.id,
                    user_from=unicode(c.user_from.user),
                    user_from_id=c.user_from.user.id,
                    user_to=unicode(c.user_to.user),
                    user_to_id=c.user_to.user.id) for c in ChallengeGame.get_active(challuser)]

        class ChallengeLaunch(BaseHandler):
            methods_allowed = ('GET',)

            def read(self, request, player_id):
                player = request.user.get_profile()
                challuser = player.get_extension(ChallengeUser)

                try:
                    player2 = Player.objects.get(pk=player_id)
                except Player.DoesNotExist:
                    return rc.NOT_FOUND

                challuser2 = player2.get_extension(ChallengeUser)

                try:
                    chall = challuser.launch_against(challuser2)
                except ChallengeException as e:
                    return {'success': False, 'error': unicode(e)}

                return {'success': True, 'challenge': chall}

        class ChallengeHandler(BaseHandler):
            methods_allowed = ('GET',)
            def read(self, request, challenge_id, action='play'):
                player = request.user.get_profile()
                challuser = player.get_extension(ChallengeUser)
                try:
                    challenge = Challenge.objects.get(pk=challenge_id)
                except Challenge.DoesNotExist:
                    return rc.NOT_FOUND

                try:
                    participant = challenge.participant_for_player(player)
                except ValueError:
                    return rc.NOT_FOUND

                if action == 'play':
                    if not challenge.is_runnable():
                        return {'success': False, 'error': 'Challenge is not runnable'}

                    if not participant.start:
                        challenge.set_start(player)

                    if challenge.is_expired_for_user(player):
                        return {'success': False, 'error': 'Challenge expired for this user'}

                    return {'success': True,
                            'status': challenge.status,
                            'from': unicode(challenge.user_from.user),
                            'to': unicode(challenge.user_to.user),
                            'date': challenge.date,
                            'seconds': challenge.time_for_user(challuser),
                            'questions': dict([(q.id ,{'text': q.text, 'answers': dict([(a.id, a.text) for a in q.answers])}) for q in challenge.questions.all()]),
                    }

                if action == 'refuse':
                    if challenge.user_to.user == challuser and challenge.is_launched():
                        challenge.refuse()
                        return {'success': True}
                    else:
                        return {'success': False, 'error': 'Cannot refuse this challenge'}
                if action == 'cancel':
                    if challenge.user_from.user == challuser and challenge.is_launched():
                        challenge.cancel()
                        return {'success': True}
                    else:
                        return {'success': False, 'error': 'Cannot cancel this challenge'}
                if action == 'accept':
                    if challenge.user_to.user == challuser and challenge.is_launched():
                        challenge.accept()
                        return {'success': True}
                    else:
                        return {'success': False, 'error': 'Cannot accept this challenge'}

                return {'success': False, 'error': 'Unknown action'}

            def create(self, request, challenge_id):
                """ Attempt to respond
                """
                player = request.user.get_profile()
                challuser = player.get_extension(ChallengeUser)
                try:
                    challenge = Challenge.objects.get(pk=challenge_id)
                except Challenge.DoesNotExist:
                    return rc.NOT_FOUND

                try:
                    p = challenge.participant_for_player(player)
                except ValueError:
                    return rc.NOT_FOUND

                if p.played:
                    return {'success': False, 'error': 'Already played'}

                data = self.flatten_dict(request.POST)
                responses = {}
                try:
                    for q in challenge.questions.all():
                        responses[q.id] = [int(a) if a else '' for a in data.get(str(q.id), '').split(',')]
                except (IndexError, ValueError):
                    return {'success': False, 'error': 'Unable to parse answers'}

                result = challenge.set_played(challuser, responses)

                return {'success': True, 'result': result}


        return {r'^challenge/list/$': ChallengesHandler,
                r'^challenge/launch/(?P<player_id>\d+)/$': ChallengeLaunch,
                r'^challenge/(?P<challenge_id>\d+)/$': ChallengeHandler,
                r'^challenge/(?P<challenge_id>\d+)/(?P<action>refuse|cancel|accept)/$': ChallengeHandler,
        }

# Hack for having participants in sync
def challenge_post_delete(sender, instance, **kwargs):
    """ For some reason, this is called twice. Needs investigantion
    Also, in django devele, on_delete=cascade will fix this hack
    """
    try:
        instance.user_from.delete()
        instance.user_to.delete()
    except: pass
models.signals.post_delete.connect(challenge_post_delete, Challenge)
