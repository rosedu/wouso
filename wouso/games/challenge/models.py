import logging
from datetime import datetime, time, timedelta
from random import shuffle
import pickle as pk
from django.db import models
from django.db.models import Q, Max
from django.utils.translation import ugettext_noop
from wouso.core.user.models import Player, InsufficientAmount
from wouso.core.qpool.models import Question
from wouso.core.qpool import get_questions_with_category
from wouso.core.game.models import Game
from wouso.core import scoring
from wouso.core.scoring.models import Formula
from wouso.interface.activity import signals


class ChallengeUser(Player):
    """ Extension of the userprofile, customized for challenge """

    last_launched = models.DateTimeField(default=datetime(1, 1, 1), blank=True, null=True)

    def can_launch(self):
        """ Check if 1 challenge per day restriction apply
        """
        now = datetime.now()
        today_start = datetime.combine(now, time())
        today_end = datetime.combine(now, time(23, 59, 59))
        if today_start <= self.last_launched <= today_end:
            return False
        return True

    def can_challenge(self, user):
        """ Check if the target user is available.
        """
        user = user.get_extension(ChallengeUser)
        if self.user == user.user:
            # Cannot challenge myself
            return False
        return True

    def has_one_more(self):
        return self.has_modifier('challenge-one-more')

    def do_one_more(self):
        try:
            modifier = self.use_modifier('challenge-one-more', 1)
        except InsufficientAmount:
            return False
        self.last_launched -= timedelta(days=-1)
        self.save()

        signal_msg = ugettext_noop('{user} used {artifact} to enable one more challenge.')
        signals.addActivity.send(sender=None, user_from=self, \
                                     user_to=self, \
                                     message=signal_msg, \
                                     arguments=dict(user=self, artifact=modifier.artifact.title), \
                                     game=ChallengeGame.get_instance())
        return True

    def can_play(self, challenge):
        return challenge.can_play(self)


class Participant(models.Model):
    user = models.ForeignKey(ChallengeUser)
    start = models.DateTimeField(null=True, blank=True)
    seconds_took = models.IntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    responses = models.TextField(default='', blank=True, null=True)
    score = models.FloatField(null=True, blank=True)

    @property
    def challenge(self):
        #return Challenge.objects.get(Q(user_from=self)|Q(user_to=self))
        try:
            return Challenge.objects.get(Q(user_from=self)|Q(user_to=self))
        except:
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
    def create(user_from, user_to):
        """ Assigns questions, and returns the number of assigned q """

        questions = [q for q in get_questions_with_category('challenge')]
        if len(questions) < 5:
            raise ValueError('Too few questions')
        shuffle(questions)

        uf, ut = Participant(user=user_from), Participant(user=user_to)
        uf.save(), ut.save()

        c = Challenge(user_from=uf, user_to=ut, date=datetime.now())
        c.save()

        # set last_launched
        user_from.last_launched = datetime.now()
        user_from.save()

        # TODO: better question selection
        #limit = 5
        for q in questions[:Challenge.LIMIT]:
            c.questions.add(q)

        return c

    @staticmethod
    def get_expired(today):
        """
        Return all expired challenges at given date.
        """
        yesterday = today + timedelta(days=-1) # TODO: use combine
        return Challenge.objects.filter(status='a', date__lt=yesterday)

    @property
    def participants(self):
        return (self.user_from, self.user_to)

    def accept(self):
        self.status = 'A'
        self.save()

    def refuse(self):
        self.status = 'R'
        self.user_from.user.last_launched = datetime(1, 1, 1)
        self.user_from.user.save()

        # send activty signal
        signal_msg = ugettext_noop('{user_to} has refused challenge from {user_from}')

        signals.addActivity.send(sender=None, user_from=self.user_to.user, \
                                     user_to=self.user_from.user, \
                                     message=signal_msg, \
                                     arguments=dict(user_to=self.user_to, user_from=self.user_from), \
                                     game=ChallengeGame.get_instance())
        self.save()

    def cancel(self):
        self.user_from.user.last_launched = datetime(1, 1, 1)
        self.user_from.user.save()
        self.delete()

    def set_start(self, user):
        """ Update user.start and set playing time to now
        This is called when one of the participants sees the challenge for the
        first time.
        After this call, challenge will be visible to him for 5 minutes
        TODO: check it hasn't been already started in the past"""
        user = user.get_extension(ChallengeUser)

        if self.user_from.user == user:
            self.user_from.start = datetime.now()
            self.user_from.save()
        elif self.user_to.user == user:
            self.user_to.start = datetime.now()
            self.user_to.save()
        else:
            pass # todo raise something

    def time_for_user(self, user):
        now = datetime.now()

        if user == self.user_from.user:
            partic = self.user_from
        elif user == self.user_to.user:
            partic = self.user_to
        else:
            return 0

        return Challenge.TIME_LIMIT - (now - partic.start).seconds

    def check_timedelta(self, user):
        """Check that the challenge form has been submitted in the allowed time"""
        user = user.get_extension(ChallengeUser)
        now = datetime.now()

        if self.user_from.user == user:
            if (now - self.user_from.start).seconds < (Challenge.TIME_LIMIT + Challenge.TIME_SAFE):
                return True
            return False
        elif self.user_to.user == user:
            if (now - self.user_to.start).seconds < (Challenge.TIME_LIMIT + Challenge.TIME_SAFE):
                return True
            return False
        else:
            pass # again, raise something

    def is_started_for_user(self, user):
        """Check if the challenge has already started for the given user"""
        user = user.get_extension(ChallengeUser)
        if self.user_from.user == user:
            if self.user_from.start is None:
                return False
            return True
        elif self.user_to.user == user:
            if self.user_to.start is None:
                return False
            return True
        else:
            pass #raise something

    def expired(self, user):
        # set winner the OTHER user, set challenge as played, score.
        if self.status == 'P':
            return
        self.status = 'P'
        exp_user = user.get_extension(ChallengeUser)
        if exp_user == self.user_from.user:
            self.user_won = self.user_to
            self.user_lost = self.user_from
        elif exp_user == self.user_to.user:
            self.user_won = self.user_from
            self.user_lost = self.user_to
        self.user_won.score = 42
        self.user_won.played = True
        self.user_won.save()
        self.user_lost.score = -1
        self.user_lost.played = True
        self.user_lost.seconds_took = (datetime.now() - user_played.start).seconds
        self.user_lost.save()
        self.winner = self.user_won.user
        scoring.score(self.user_won.user, ChallengeGame, 'chall-won',
            external_id=self.id, points=self.user_won.score, points2=self.user_lost.score)
        scoring.score(self.user_lost.user, ChallengeGame, 'chall-lost',
            external_id=self.id, points=self.user_lost.score, points2=self.user_lost.score)

        # send activty signal to the winner
        signal_msg = ugettext_noop('Challenge to {user_to} from {user_from} has expired and it was automatically settled.'\
            ' {user_won} won.')

        signals.addActivity.send(sender=None, user_from=exp_user, \
                                     user_to=self.user_won.user, \
                                     message=signal_msg, \
                                     arguments=dict(user_to=self.user_to, user_from=self.user_from, user_won=self.user_won), \
                                     game=ChallengeGame.get_instance())
        self.save()

    def extraInfo(self, user_won, user_lost):
        '''returns a string with extra info for a string such as User 1 finished the challenge in $SECONDS seconds
        (or $MINUTES minutes and seconds) and scored X points)'''

        def formatTime(seconds):
            if seconds < 60:
                return "%d seconds" % seconds
            elif seconds == 60:
                return '1 minute'
            elif seconds % 60 == 0:
                return '%d minutes' % (seconds/60)
            elif 60 < seconds < 120:
                return '1 minute and %d seconds' % (seconds % 60)
            return '%d minutes and %d seconds' % (seconds / 60, seconds % 60)

        return '%.2fp (in %s) - %.2fp (in %s)' % (user_won.score, formatTime(user_won.seconds_took),
                                                    user_lost.score, formatTime(user_lost.seconds_took))

    def played(self):
        """ Both players have played, save and score """
        for participant in self.participants:
            try:
                answers = pk.loads(str(participant.responses))
            except:
                answers = {}
            participant.score = self._calculate_points(answers)
            participant.save()

        if self.user_to.score > self.user_from.score:
            result = (self.user_to, self.user_from)
        elif self.user_from.score > self.user_to.score:
            result = (self.user_from, self.user_to)
        else: #draw game
            result = 'draw'

        if result == 'draw':
            self.status = 'D'
            scoring.score(self.user_to.user, ChallengeGame, 'chall-draw')
            scoring.score(self.user_from.user, ChallengeGame, 'chall-draw')
            # send activty signal
            signal_msg = ugettext_noop('Draw result between {user_to} and {user_from}:\n{extra}')
            signals.addActivity.send(sender=None, user_from=self.user_to.user, \
                                     user_to=self.user_from.user, \
                                     message=signal_msg, \
                                     arguments=dict(user_to=self.user_to, user_from=self.user_from,
                                                    extra=self.extraInfo(self.user_won, self.user_lost)),\
                                     game=ChallengeGame.get_instance())
        else:
            self.status = 'P'
            self.user_won, self.user_lost = result
            self.winner = self.user_won.user
            scoring.score(self.user_won.user, ChallengeGame, 'chall-won',
                external_id=self.id, points=self.user_won.score, points2=self.user_lost.score)
            scoring.score(self.user_lost.user, ChallengeGame, 'chall-lost',
                external_id=self.id, points=self.user_lost.score, points2=self.user_lost.score)
            # send activty signal
            signal_msg = ugettext_noop('{user_won} won challenge with {user_lost}: {extra}')
            signals.addActivity.send(sender=None, user_from=self.user_from.user, \
                                     user_to=self.user_to.user, \
                                     message=signal_msg, arguments=dict(user_won=self.user_won, user_lost=self.user_lost,
                                                                        extra=self.extraInfo(self.user_won, self.user_lost)), \
                                     game=ChallengeGame.get_instance())
        self.save()

    def _calculate_points(self, responses):
        """ Response contains a dict with question id and checked answers ids.
        Example:
            1 : {14}, - has answered answer with id 14 at the question with id 1
        """
        points = 0.0
        for r, v in responses.iteritems():
            checked = missed = 0
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
        return points

    def set_played(self, user, responses):
        """ Set user's results. If both users have played, also update self and activity. """
        if self.user_to.user == user:
            user_played = self.user_to
        elif self.user_from.user == user:
            user_played = self.user_from
        else:
            logging.error("Invalid user")
            return

        user_played.seconds_took = (datetime.now() - user_played.start).seconds
        user_played.played = True
        user_played.responses = pk.dumps(responses)
        user_played.save()

        if self.user_to.played and self.user_from.played:
            self.played()

        return {'points': self._calculate_points(responses)}

    def can_play(self, user):
        """ Check if user can play this challenge"""
        if self.user_to.user != user and self.user_from.user != user:
            return False

        if self.user_to == user:
            if self.played_to:
                return False

        elif self.user_from == user:
            if self.played_from:
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
        self._meta.get_field('verbose_name').default = "Challenge"
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
                Q(user=user, played=False))]
        except Participant.DoesNotExist:
            challs = []
        return challs

    @staticmethod
    def get_played(user):
        """ Return a list of played (scored TODO) challenges for a user """
        try:
            challs = [p.challenge for p in Participant.objects.filter(
                Q(user=user, played=True))]
        except Participant.DoesNotExist:
            challs = []
        return challs

    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        chall_game = kls.get_instance()
        fs.append(Formula(id='chall-won', formula='points=3',
            owner=chall_game.game,
            description='Points earned when winning a challenge')
        )
        fs.append(Formula(id='chall-lost', formula='points=-1',
            owner=chall_game.game,
            description='Points earned when losing a challenge')
        )
        fs.append(Formula(id='chall-draw', formula='points=1',
            owner=chall_game.game,
            description='Points earned when drawing a challenge')
        )
        return fs
    @classmethod
    def get_modifiers(kls):
        """
        Challenge modifiers:
            challenge-one-more: if applied, user can challenge twice a day.
        """
        return ['challenge-one-more']

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return None

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

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
