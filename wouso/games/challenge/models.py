import random
from datetime import datetime, time, timedelta, date
from random import shuffle
import pickle as pk
import sys
from django.db import models
from django.db.models import Q, Avg
from django.utils.translation import ugettext_noop, ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from wouso.core.user.models import Player
from wouso.core.magic.manager import InsufficientAmount
from wouso.core.qpool.models import Question
from wouso.core.qpool import get_questions_with_category
from wouso.core.game.models import Game
from wouso.core import scoring, signals
from wouso.core.god import God
from wouso.interface.apps.messaging.models import Message
import logging


class ChallengeException(Exception):
    pass


class ChallengeUser(Player):
    """ Extension of the userprofile, customized for challenge """

    last_launched = models.DateTimeField(blank=True, null=True)

    def is_eligible(self):
        return God.user_is_eligible(self, ChallengeGame)

    def can_launch(self):
        """ Check if 1 challenge per day restriction apply
        """
        now = datetime.now()
        today_start = datetime.combine(now, time())
        today_end = datetime.combine(now, time(23, 59, 59))
        logging.info("today_start: %s, today_end: %s, self.last_launched: %s" % (today_start, today_end, self.last_launched))
        if self.magic.has_modifier('challenge-cannot-challenge'):
            return False
        if not self.last_launched:
            return True
        if today_start <= self.last_launched <= today_end:
            return False
        return True

    def has_enough_points(self):
        """ Check if the user has 30 points to challenge
        """
        REQ_POINTS = 30
        return self.points >= REQ_POINTS

    def in_same_division(self, user):
        from wouso.interface.top.models import TopUser
        position_diff = abs(self.get_extension(TopUser).position - user.get_extension(TopUser).position)
        if position_diff <= 20:
            return True
        return False

    def can_challenge(self, user):
        """ Check if the target user is available.
        """
        user = user.get_extension(ChallengeUser)
        if self.user == user.user:
            # Cannot challenge myself
            logging.info("User cannot challenge because it is the same user.")
            return False
        if user.magic.has_modifier('challenge-cannot-be-challenged'):
            logging.info("User cannot challenge due to magic modifier.")
            return False
        return God.user_can_interact_with(self, user, game=ChallengeGame)

    def has_one_more(self):
        return self.magic.has_modifier('challenge-one-more')

    def do_one_more(self):
        try:
            modifier = self.magic.use_modifier('challenge-one-more', 1)
        except InsufficientAmount:
            return False
        self.set_last_launched(None)
        self.save()

        signal_msg = ugettext_noop('used {artifact} to enable one more challenge.')
        signals.addActivity.send(sender=None, user_from=self,
                                 user_to=self,
                                 message=signal_msg,
                                 arguments=dict(artifact=modifier.artifact.title),
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

        if not self.in_same_division(destination):
            raise ChallengeException('You are not in the same division')

        if not self.can_challenge(destination):
            raise ChallengeException('Player cannot launch against this opponent')

        return Challenge.create(user_from=self, user_to=destination)

    def set_last_launched(self, value):
        logging.info("set last launched of %s to %s" % (hex(id(self)), value))
        self.last_launched = value
        self.save()

    def get_all_challenges(self):
        return Challenge.objects.exclude(status=u'L').filter(Q(user_from__user=self) | Q(user_to__user=self))

    def get_won_challenges(self):
        return self.get_all_challenges().filter(winner=self)

    def get_lost_challenges(self):
        return self.get_all_challenges().exclude(winner=self).exclude(status=u'R').exclude(status=u'D')

    def get_draw_challenges(self):
        return self.get_all_challenges().filter(status=u'D')

    def get_refused_challenges(self):
        return self.get_all_challenges().filter(status=u'R')

    def get_win_percentage(self):
        w = self.get_won_challenges().count()
        d = self.get_draw_challenges().count()
        l = self.get_lost_challenges().count()
        # 1 draw counts as 1/2 win, 1/2 loss
        return 0 if w + d == 0 else (w + d / 2.0) / (w + l + d) * 100

    def get_random_opponent(self):
        players = ChallengeUser.objects.exclude(user=self.user)
        players = players.exclude(race__can_play=False)
        players = [p for p in players if self.can_challenge(p) and self.in_same_division(p)]
        if not players:
            return False
        # selects the user to be challenged
        import random
        i = random.randrange(0, len(players))
        return players[i]

    def get_related_challenges(self, target_user):
        # Gets the challenges between self and target_user
        chall_total = Challenge.objects.filter(Q(user_from__user=self) |
                                               Q(user_to__user=self)).exclude(status=u'L')
        chall_total = chall_total.filter(Q(user_from__user=target_user) |
                                         Q(user_to__user=target_user)).order_by('-date')
        return chall_total

    def get_stats(self):
        chall_total = self.get_all_challenges()
        chall_won = self.get_won_challenges()
        chall_sent = chall_total.filter(user_from__user=self)
        chall_rec = chall_total.filter(user_to__user=self)

        n_chall_sent = chall_sent.count()
        n_chall_rec = chall_rec.count()
        n_chall_played = chall_sent.count() + chall_rec.count()
        n_chall_won = chall_won.count()
        n_chall_ref = self.get_refused_challenges().count()
        all_participation = Participant.objects.filter(user=self)

        opponents_from = list(set(map(lambda x: x.user_to.user, chall_sent)))
        opponents_to = list(set(map(lambda x: x.user_from.user, chall_rec)))
        opponents = list(set(opponents_from + opponents_to))

        result = []
        for op in opponents:
            chall_against_op = chall_total.filter(Q(user_to__user=op) | Q(user_from__user=op))
            won = chall_against_op.filter(Q(status=u'P') & Q(winner=self)).count()
            lost = chall_against_op.filter(Q(status=u'P') & Q(winner=op)).count()
            draw = chall_against_op.filter(Q(status=u'D')).count()
            refused = chall_against_op.filter(Q(status=u'R')).count()
            total = won + lost + draw + refused
            result.append((op, won, lost, draw, refused, total))

        # Sort results by 'total'
        result = sorted(result, key=lambda by: by[5], reverse=True)

        average_time = all_participation.aggregate(Avg('seconds_took'))['seconds_took__avg']
        average_score = all_participation.aggregate(Avg('score'))['score__avg']

        if average_time is None:
            average_time = 0
        if average_score is None:
            average_score = 0

        win_percentage = self.get_win_percentage()

        stats = dict(n_chall_played=n_chall_played, n_chall_won=n_chall_won,
                     n_chall_sent=n_chall_sent, n_chall_rec=n_chall_rec,
                     n_chall_ref=n_chall_ref, current_player=self,
                     average_time=average_time, average_score=average_score,
                     win_percentage=win_percentage, opponents=result)
        return stats

Player.register_extension('challenge', ChallengeUser)


class Participant(models.Model):
    user = models.ForeignKey(ChallengeUser)
    start = models.DateTimeField(null=True, blank=True)
    seconds_took = models.IntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    responses = models.TextField(default='', blank=True, null=True)
    # score = models.FloatField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    @property
    def challenge(self):
        try:
            return Challenge.objects.get(Q(user_from=self) | Q(user_to=self))
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
    owner = models.ForeignKey(Game, null=True, blank=True)

    nr_q = 0
    LIMIT = 5
    TIME_LIMIT = 300  # seconds
    TIME_SAFE = 10    # seconds more
    WARRANTY = True   # on/off switch
    SCORING = True    # on/off switch for rewarding challenges

    @classmethod
    def create(cls, user_from, user_to, ignore_questions=False):
        """ Assigns questions, and returns the number of assigned q """
        questions = [q for q in get_questions_with_category('challenge')]
        if (len(questions) < cls.LIMIT) and not ignore_questions:
            raise ChallengeException('Too few questions')
        shuffle(questions)

        questions_qs = questions[:cls.LIMIT]
        challenge = cls.create_custom(user_from, user_to, questions_qs)

        # set last_launched
        user_from = user_from.get_extension(ChallengeUser)
        user_from.set_last_launched(datetime.now())

        return challenge

    @classmethod
    def create_custom(cls, player_from, player_to, questions_qs, game=None):
        user_from, user_to = player_from.get_extension(ChallengeUser), player_to.get_extension(ChallengeUser)
        uf, ut = Participant.objects.create(user=user_from), Participant.objects.create(user=user_to)

        c = Challenge.objects.create(user_from=uf, user_to=ut, date=datetime.now(), owner=game)
        for q in questions_qs:
            c.questions.add(q)

        c.manager.created()
        return c

    @staticmethod
    def get_expired(today):
        """
        Return all expired candidate challenges at given date.
        """
        yesterday = today + timedelta(days=-1)
        return Challenge.objects.filter(date__lt=yesterday).filter(Q(status='A') | Q(status='L'))

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

    @property
    def manager(self):
        if self.owner is None or self.owner.name == 'ChallengeGame':
            return ChallengeGame.get_manager(self)
        return self.owner.get_real_object().get_manager(self)

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
        self.manager.accept()

    def refuse(self, auto=False):
        self.status = 'R'
        self.save()
        self.manager.refuse(auto)

    def cancel(self):
        self.manager.cancel()
        self.user_from.user.set_last_launched(None)
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

    def set_won_by_player(self, player):
        if self.user_from.user == player:
            self.user_from.score = 1
            self.user_to.score = 0
        else:
            self.user_from.score = 0
            self.user_to.score = 1

        self.user_from.played = True
        self.user_to.played = True

        # process expired activity
        self.played()

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

        tlimit = scoring.timer(user, ChallengeGame, 'chall-timer', level=user.level_no)

        return tlimit - (now - partic.start).seconds

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
        result = self.manager.get_result()

        if result == 'draw':
            self.status = 'D'
        else:
            self.status = 'P'
            self.user_won, self.user_lost = result
            self.winner = self.user_won.user
        self.save()

        self.manager.handle_result()
        self.manager.score()

    @classmethod
    def _calculate_points(cls, responses):
        """ Response contains a dict with question id and checked answers ids.
        Example:
            {1 : [14,], ...}, - has answered answer with id 14 at the question with id 1
        """
        points = 0.0
        results = {}
        for r, v in responses.iteritems():
            checked, missed, wrong = 0, 0, 0
            q = Question.objects.get(id=r)
            for a in q.answers.all():
                if a.correct:
                    if a.id in v:
                        checked += 1
                    else:
                        missed += 1
                elif a.id in v:
                    wrong += 1
            correct_count = len([a for a in q.answers if a.correct])
            wrong_count = len([a for a in q.answers if not a.correct])
            if correct_count == 0:
                qpoints = 1 if (len(v) == 0) else 0
            elif wrong_count == 0:
                qpoints = 1 if (len(v) == q.answers.count()) else 0
            else:
                qpoints = float(checked) / correct_count - float(wrong) / wrong_count
            qpoints = qpoints if qpoints > 0 else 0
            points += qpoints
            results[r] = ((checked, correct_count))
        return {'points': int(100.0 * points), 'results': results}

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
            results = Challenge._calculate_points(responses)
            user_played.score = results['points']
        user_played.save()

        if self.user_to.played and self.user_from.played:
            self.played()

        if exp:
            results = {}
            results['results'] = {}
            results['points'] = '0.0 (expired)'
        return results

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

    def is_draw(self):
        return self.status == 'D'

    def is_played(self):
        return self.status == 'P'

    def title(self):
        return u"%s vs %s" % (self.user_from, self.user_to)

    def __unicode__(self):
        return "%s vs %s (%s) - %s [%d] " % (
            unicode(self.user_from),
            unicode(self.user_to),
            self.date,
            self.status,
            self.questions.count())


class ChallengeManager(object):
    def __init__(self, challenge):
        self.challenge = challenge

    def created(self):
        pass

    def accept(self):
        pass

    def refuse(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    def get_result(self):
        raise NotImplementedError

    def handle_result(self):
        """ Called after status is one of: 'D', 'P'
        """
        pass

    def score(self):
        raise NotImplementedError


class DefaultChallengeManager(ChallengeManager):
    def created(self):
        if self.challenge.WARRANTY:
            # take 3 points from user_from
            scoring.score(self.challenge.user_from.user, ChallengeGame, 'chall-warranty', external_id=self.challenge.id)

    def accept(self):
        if self.challenge.WARRANTY:
            # take warranty from user_to
            scoring.score(self.challenge.user_to.user, ChallengeGame, 'chall-warranty', external_id=self.challenge.id)

    def refuse(self, auto):
        self.challenge.user_from.user.set_last_launched(None)

        # send activity signal
        if auto:
            signal_msg = ugettext_noop('has refused challenge from {chall_from} (expired)')
        else:
            signal_msg = ugettext_noop('has refused challenge from {chall_from}')
        action_msg = 'chall-refused'
        signals.addActivity.send(sender=None,
                                 user_from=self.challenge.user_to.user,
                                 user_to=self.challenge.user_from.user,
                                 message=signal_msg,
                                 arguments=dict(chall_from=self.challenge.user_from),
                                 action=action_msg,
                                 game=ChallengeGame.get_instance())
        self.challenge.save()
        if self.challenge.WARRANTY:
            # give warranty back to initiator
            scoring.unset(self.challenge.user_from.user, ChallengeGame, 'chall-warranty', external_id=self.challenge.id)

    def cancel(self):
        if self.challenge.WARRANTY:
            # give warranty back to initiator
            scoring.unset(self.challenge.user_from.user, ChallengeGame, 'chall-warranty', external_id=self.challenge.id)

    def get_result(self):
        for u in (self.challenge.user_to, self.challenge.user_from):
            if u.user.magic.has_modifier('challenge-always-lose'):
                u.score = -1

        if self.challenge.user_to.score > self.challenge.user_from.score:
            result = (self.challenge.user_to, self.challenge.user_from)
        elif self.challenge.user_from.score > self.challenge.user_to.score:
            result = (self.challenge.user_from, self.challenge.user_to)
        else:  # draw game
            result = 'draw'

        return result

    def handle_result(self):
        if self.challenge.status == 'D':
            action_msg = "chall-draw"
            signal_msg = ugettext_noop('draw result between {user_from} and {user_to}:\n{extra}')
            signals.addActivity.send(sender=None, user_from=self.challenge.user_to.user,
                                     user_to=self.challenge.user_from.user,
                                     message=signal_msg,
                                     arguments=dict(user_to=self.challenge.user_to, user_from=self.challenge.user_from,
                                                    extra=self.challenge.extraInfo(self.challenge.user_from, self.challenge.user_to)),
                                     action=action_msg,
                                     game=ChallengeGame.get_instance())
        elif self.challenge.status == 'P':
            action_msg = "chall-won"
            signal_msg = ugettext_noop('won challenge with {user_lost}: {extra}')
            signals.addActivity.send(sender=None, user_from=self.challenge.user_won.user,
                                     user_to=self.challenge.user_lost.user,
                                     message=signal_msg,
                                     arguments=dict(user_lost=self.challenge.user_lost, id=self.challenge.id,
                                                    extra=self.challenge.extraInfo(self.challenge.user_won, self.challenge.user_lost)),
                                     action=action_msg,
                                     game=ChallengeGame.get_instance())

    def score(self):
        if not self.challenge.SCORING:
            return

        for u in (self.challenge.user_to, self.challenge.user_from):
                u.percents = 100

        if self.challenge.status == 'D':
            scoring.score(self.challenge.user_to.user, ChallengeGame, 'chall-draw', percents=self.challenge.user_to.percents)
            scoring.score(self.challenge.user_from.user, ChallengeGame, 'chall-draw', percents=self.challenge.user_from.percents)
        else:
            diff_race = self.challenge.user_won.user.race != self.challenge.user_lost.user.race
            diff_class = self.challenge.user_won.user.group != self.challenge.user_lost.user.group
            diff_race = 1 if diff_race else 0
            diff_class = 1 if diff_class else 0
            winner_points = self.challenge.user_won.user.points
            loser_points = self.challenge.user_lost.user.points

            # Check for charge
            if self.challenge.user_won.user.magic.has_modifier('challenge-affect-scoring-won'):
                self.challenge.user_won.percents += self.challenge.user_won.user.magic.modifier_percents('challenge-affect-scoring-won') - 100

            # Check for weakness
            if self.challenge.user_won.user.magic.has_modifier('challenge-affect-scoring-lost'):
                self.challenge.user_won.percents += self.challenge.user_won.user.magic.modifier_percents('challenge-affect-scoring-lost') - 100

            # Check for frenzy on the winning player
            if self.challenge.user_won.user.magic.has_modifier('challenge-affect-scoring'):
                self.challenge.user_won.percents += self.challenge.user_won.user.magic.modifier_percents('challenge-affect-scoring') - 100

            if self.challenge.WARRANTY:
                # warranty not affected by percents
                scoring.score(self.challenge.user_won.user, ChallengeGame, 'chall-warranty-return', external_id=self.challenge.id)

            scoring.score(self.challenge.user_won.user, ChallengeGame, 'chall-won',
                          external_id=self.challenge.id, percents=self.challenge.user_won.percents,
                          points=self.challenge.user_won.score, points2=self.challenge.user_lost.score,
                          different_race=diff_race, different_class=diff_class,
                          winner_points=winner_points, loser_points=loser_points)

            # Check for frenzy on the losing player
            if self.challenge.user_lost.user.magic.has_modifier('challenge-affect-scoring'):
                self.challenge.user_lost.percents += self.challenge.user_lost.user.magic.modifier_percents('challenge-affect-scoring') - 100

            # Check for spell evade
            if self.challenge.user_lost.user.magic.has_modifier('challenge-evade'):
                random.seed()
                if random.random() < 0.20:
                    # He's lucky, no penalty, return warranty
                    scoring.score(self.challenge.user_lost.user, ChallengeGame, 'chall-warranty-return', external_id=self.challenge.id)
                    Message.send(sender=None, receiver=self.challenge.user_lost.user, subject="Challenge evaded", text="You have just evaded losing points in a challenge")

            scoring.score(self.challenge.user_lost.user, ChallengeGame, 'chall-lost',
                          external_id=self.challenge.id, percents=self.challenge.user_lost.percents,
                          points=self.challenge.user_lost.score, points2=self.challenge.user_lost.score)


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
                Q(user_id=user.id, played=False)).order_by('-id') if p.challenge.is_launched() or p.challenge.is_runnable()]
        except Participant.DoesNotExist:
            challs = []
        return challs

    @staticmethod
    def get_played(user):
        """ Return a list of played (scored TODO) challenges for a user """
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user_id=user.id, played=True)).order_by('-id')]
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
        fs.append(dict(name='chall-won', expression='points=6+{different_race}+{different_class}',
                       owner=chall_game.game,
                       description='Points earned when winning a challenge. Arguments: different_race (int 0,1), different_class (int 0,1)'))
        fs.append(dict(name='chall-lost', expression='points=2',
                       owner=chall_game.game,
                       description='Points earned when losing a challenge'))
        fs.append(dict(name='chall-draw', expression='points=4',
                       owner=chall_game.game,
                       description='Points earned when drawing a challenge'))
        fs.append(dict(name='chall-warranty', expression='points=-3',
                       owner=chall_game.game,
                       description='Points taken as a warranty for challenge'))
        fs.append(dict(name='chall-warranty-return', expression='points=3',
                       owner=chall_game.game,
                       description='Points given back as a warranty taken for challenge'))
        fs.append(dict(name='chall-timer',
                       expression='tlimit=300 - 5 * ({level} - 1)', owner=chall_game.game,
                       description='Seconds left for a user in challenge'))
        return fs

    @classmethod
    def get_modifiers(kls):
        """
        Challenge game modifiers
        """
        return ['challenge-one-more',  # challenge twice a day, positive
                'challenge-cannot-be-challenged',  # reject incoming challenges, negative
                'challenge-cannot-challenge',  # reject outgoing challenges, negative
                'challenge-always-lose',  # lose regardless the result, negative
                'challenge-affect-scoring',  # affect scoring by positive/negative percent
                'challenge-affect-scoring-won',  # affect scoring by positive/negative percent for win challenges
                'challenge-evade',  # 33% chance player does not lose points in a challenge
                ]

    @classmethod
    def management_task(cls, now=None, stdout=sys.stdout):
        now = now if now else datetime.now()
        today = now.date()
        challenges = Challenge.get_expired(today)
        stdout.write(' Updating %d expired challenges (at %s)\n' % (len(challenges), today))
        for c in challenges:
            if c.is_launched():
                # launched before yesterday, automatically refuse
                c.refuse(auto=True)
            else:
                # launched and accepted before yesterday, but not played by both
                c.set_expired()

    @classmethod
    def get_api(kls):
        from api import ChallengesHandler, ChallengeLaunch, ChallengeHandler, ChallengeGetRandom

        return {r'^challenge/list/$': ChallengesHandler,
                r'^challenge/random/$': ChallengeGetRandom,
                r'^challenge/launch/(?P<player_id>\d+)/$': ChallengeLaunch,
                r'^challenge/(?P<challenge_id>\d+)/$': ChallengeHandler,
                r'^challenge/(?P<challenge_id>\d+)/(?P<action>refuse|cancel|accept)/$': ChallengeHandler,
                }

    @classmethod
    def get_manager(cls, challenge):
        return DefaultChallengeManager(challenge)


# Hack for having participants in sync
def challenge_post_delete(sender, instance, **kwargs):
    """ For some reason, this is called twice. Needs investigantion
    Also, in django devele, on_delete=cascade will fix this hack
    """
    try:
        instance.user_from.delete()
        instance.user_to.delete()
    except:
        pass
models.signals.post_delete.connect(challenge_post_delete, Challenge)
