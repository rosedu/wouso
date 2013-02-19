from django.db import models
from django.db.models import Q, Max
import logging
from wouso.core.config.models import IntegerSetting
from wouso.core.game.models import Game
from wouso.core.user.models import Player
from wouso.games.challenge.models import Challenge, ChallengeUser


class GrandChallengeUser(Player):
    """ Extension of the user profile for GrandChallenge """
    lost = models.IntegerField(default=0)
    last_round = models.IntegerField(default=0)

    def get_challenges(self):
        """
        Return a queryset of grandchallenges for this player
        """
        return Challenge.objects.filter(id__in=GrandChallenge.objects.filter(Q(challenge__user_from__user__id=self.id)|Q(challenge__user_to__user__id=self.id)).order_by('round').values('challenge'))

    def get_active(self):
        """
        Return a list of active GrandChallenges for this user
        """
        return self.get_challenges().filter(status='A')

    def get_played(self):
        """
        Return a list of played GrandChallenges, ordered by round
        """
        return self.get_challenges().filter(status__in=('D', 'P'))

    def increase_lost(self):
        self.lost += 1
        self.save()

    def set_last_round(self, round_number):
        self.last_round = round_number
        self.save()

class GrandChallenge(models.Model):
    challenge = models.ForeignKey(Challenge, blank=True, null=True)
    round = models.IntegerField(blank=True, null=True)

    ALL = []
    OUT_PLAY = []
    CHALLENGES= []

    def __oldinit__(self, user_from, user_to):
        # TODO: change this constructor to a classmethod
        if not GrandChallengeGame.is_final() and not GrandChallengeGame.is_winner():
            self.branch = max(user_from.lost, user_to.lost)
        else:
            self.branch = min(user_from.lost, user_to.lost)
        self.user_from = user_from
        self.user_to = user_to
        self.__class__.ALL.append(self)
        self.won, self.lost = None, None
        self.active = True
        self.round_number = None
        challenge_user_to = user_to.user.get_profile().get_extension(ChallengeUser)
        challenge_user_from = user_from.user.get_profile().get_extension(ChallengeUser)
        chall = Challenge.create(challenge_user_from, challenge_user_to)
        chall.accept()
        self.challenge_id = chall.id
        self.__class__.CHALLENGES.append(chall.id)

    @classmethod
    def create(cls, user_from, user_to, round):
        """ Create a new Challenge and automatically accept it.
        """
        grand_challenge = cls.objects.create(round=round)
        user_from = user_from.user.get_profile()
        user_to = user_to.user.get_profile()
        grand_challenge.challenge = Challenge.create(user_from.get_extension(ChallengeUser), user_to.get_extension(ChallengeUser))
        grand_challenge.challenge.accept()
        grand_challenge.save()
        return grand_challenge

    @classmethod
    def get_challenges(cls):
        return cls.ALL

    @classmethod
    def active(cls):
        return filter(lambda c: c.active, cls.ALL)

    @classmethod
    def all_done(cls):
        for i in cls.CHALLENGES:
            x = Challenge.objects.get(id = i)
            if x.status != "P":
                return False
        return True

    def play(self, round_number):
        winner = Challenge.objects.get(id= self.challenge_id).winner #trebuie generat de joc

        if winner.user == self.user_from.user:
            self.won = self.user_from
            self.lost = self.user_to
            self.user_to.lost += 1
        else:
            self.won = self.user_to
            self.lost = self.user_from
            self.user_from.lost += 1
        self.active = False
        self.round_number = round_number

    @classmethod
    def played_with(cls, user):
        ret = []
        for c in [c for c in cls.ALL if not c.active]:
            if c.user_from == user:
                ret.append(c.user_to)
            elif c.user_to == user:
                ret.append(c.user_from)
        return ret

    @classmethod
    def joaca(cls, round_number):
        for c in GrandChallenge.active():

            #numarul rundei...
            c.play(round_number)
            if(c.lost.lost == 2):
                cls.OUT_PLAY.append(c.lost)
                #print c.lost


    @classmethod
    def clasament(cls):
        arb_win  = GrandChallengeGame.eligible(0)
        arb_lose = GrandChallengeGame.eligible(1)
        if(len(arb_win) == 1):
            cls.OUT_PLAY.append(arb_win[0])
        if(len(arb_lose) == 1):
            cls.OUT_PLAY.append(arb_lose[0])
        results = cls.OUT_PLAY
        results.reverse()
        return results


class Round(object):
    def __init__(self, round_number):
        self.round_number = int(round_number)

    def challenges(self):
        """
         Return a list of challenges in this round, ordered by status
        """
        return [gc.challenge for gc in GrandChallenge.objects.filter(round=self.round_number).order_by('challenge__status')]

    def info(self):
        """
         Return a dictionary with information about this round
        """
        return {}

    def participants(self):
        ps = set([c.user_from.user for c in self.challenges()] + [c.user_to.user for c in self.challenges()])
        ps = map(lambda a: a.get_extension(GrandChallengeUser), ps)
        return ps

    def rounds(self):
        """
        Return a list of previous rounds, as an iterator
        """
        if self.round_number > 0:
           for i in range(self.round_number):
               yield Round(i + 1)

    def __repr__(self):
        return '<' + 'Round ' + unicode(self.round_number) + '>'


class GrandChallengeGame(Game):
    ALL = []
    round_number = 0

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "GrandChallenges"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "grandchallenge_index_view"
        super(GrandChallengeGame, self).__init__(*args, **kwargs)

    @classmethod
    def base_query(cls):
        return GrandChallengeUser.objects.exclude(user__is_superuser=True).exclude(race__can_play=False)

    @classmethod
    def is_started(cls):
        setting_round = IntegerSetting.get('gc_round')
        return setting_round.get_value() > 0

    @classmethod
    def reset(cls):
        """
        Reset a GC game, set every user lost to 0
        """
        GrandChallenge.objects.all().delete()
        GrandChallengeUser.objects.update(lost=0, last_round=0)
        cls.set_current_round(0)

    @classmethod
    def create_users(cls):
        """
         Create GrandChallengeUser extensions for all eligibile players.
        """
        for p in Player.objects.exclude(race__can_play=False):
            p.get_extension(GrandChallengeUser)

    @classmethod
    def start(cls):
        """
         Create challenges for each consecutive players. Return a list of created challenges.
        """
        cls.create_users()
        challenges = []
        round = 1
        last = None
        for user in cls.base_query():
            u = user.user.get_profile()
            if last is None:
                last = u
            else:
                c = GrandChallenge.create(u, last, round)
                challenges.append(c)
                last = None

        setting_round = IntegerSetting.get('gc_round')
        setting_round.set_value(round)
        return challenges

    @classmethod
    def eligible(cls, lost_count):
        """ Return a queryset with players of lost_count
        """
        return cls.base_query().filter(lost=lost_count)

    @classmethod
    def is_final(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        if (len(arb_win) == 1) and (len(arb_lose) == 1):
            return True
        return False

    @classmethod
    def final_round(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        GrandChallenge(arb_win[0], arb_lose[0])

    @classmethod
    def final_second_round(cls):
        GrandChallengeGame.play_round(1)

    @classmethod
    def is_winner(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        if (len(arb_win) == 0) and (len(arb_lose) == 2):
            return False
        return True

    @classmethod
    def is_finished(cls):
        arb_win  = cls.eligible(0)
        arb_lose = cls.eligible(1)
        if len(arb_win) == 0 or (len(arb_win) == 1 and len(arb_lose) != 1):
            return True
        return False

    @classmethod
    def play_round(cls, lost_count, round_number):
        """
        Create new challenges.
        """
        if lost_count == 0:
            all = GrandChallengeGame.eligible(0)
        elif lost_count == 1:
            all = GrandChallengeGame.eligible(1)

        all = list(all)
        challenges = []
        while len(all):
            u = all[0]
            played_with = GrandChallenge.played_with(u)

            adversari = [eu for eu in all if ((eu.lost == u.lost) and (eu != u) and ((eu not in played_with) or (eu == all[-1])) )]
            if not len(adversari):
                break

            try:
                adversar = adversari[0]
                all.remove(adversar)
                all.remove(u)
                c = GrandChallenge.create(u, adversar, round_number)
                challenges.append(c)
            except Exception as e:
                logging.exception(e)
        return challenges

    @classmethod
    def set_current_round(cls, number):
        setting_round = IntegerSetting.get('gc_round')
        setting_round.set_value(number)

    @classmethod
    def get_current_round(cls):
        setting_round = IntegerSetting.get('gc_round')
        round = setting_round.get_value()
        if round == 0:
            return None
        return cls.get_round(round)

    @classmethod
    def get_round(cls, round):
        return Round(round_number=round)

    @classmethod
    def get_winner(cls):
        """
        Return gc winner
        """
        if cls.is_finished():
            final_gc = GrandChallenge.objects.filter(round=cls.get_current_round().round_number)[0]
            return final_gc.challenge.winner.user.get_profile()
        return None

    @classmethod
    def force_round_close(cls, round):
        """
         Finish every challenge in the round
        """
        for c in round.challenges():
            if c.is_runnable():
                c.set_expired()
            if c.is_draw():
                # Temporary hack FIXME
                if c.user_from.seconds_took < c.user_to.seconds_took:
                    c.set_won_by_player(c.user_from.user)
                else:
                    c.set_won_by_player(c.user_to.user)

            gc_user_from = c.user_from.user.get_extension(GrandChallengeUser)
            gc_user_to = c.user_to.user.get_extension(GrandChallengeUser)

            # Upgrade lost count
            if c.user_from.user == c.winner:
                if gc_user_to.last_round < round.round_number:
                    gc_user_to.increase_lost()
            elif c.user_to.user == c.winner:
                if gc_user_from.last_round < round.round_number:
                    gc_user_from.increase_lost()

            gc_user_from.set_last_round(round.round_number)
            gc_user_to.set_last_round(round.round_number)

    @classmethod
    def round_next(cls):
        """
         Progress to next round
        """
        if cls.is_finished():
            logging.error('Grand challenge finished.')
            return None

        round = cls.get_current_round()
        cls.force_round_close(round)

        challenges = []
        if cls.is_final():
            # Only two players left in the game
            arb_win  = cls.eligible(0)
            arb_lose = cls.eligible(1)
            challenges.append(GrandChallenge.create(arb_win[0], arb_lose[0], round.round_number + 1))
        else:
            # More than two players, create new challenges
            if round.round_number % 2 == 1:
                challenges += cls.play_round(1, round.round_number + 1)
                challenges += cls.play_round(0, round.round_number + 1)
            else:
                challenges += cls.play_round(1, round.round_number + 1)

        if challenges:
            # Update round number
            round.round_number += 1
            cls.set_current_round(round.round_number)
        logging.debug('Played round %s' % round.round_number)
        return round

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None
