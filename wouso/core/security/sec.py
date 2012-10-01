from django.db.models import Q
from wouso.core.app import App
from wouso.core.scoring.models import Coin
from models import SecurityConfig
from wouso.games.challenge.models import Challenge, ChallengeUser
from wouso.interface.activity import signals

class SecurityInspector:
    #global check function dispatcher
    @classmethod
    def check(cls, rule, **kwargs):
        #convert - to _ from id
        #Ex: chall-was-set-up -> chall_was_set_up
        return getattr(cls, rule.id.replace('-', '_'), False)(**kwargs)

    @classmethod
    def chall_was_set_up(cls, **kwargs):
        """Parse the chall-won activity message to
        check the time it took for the loser to finish the challenge"""
        suspect = kwargs.get('user_to', None)
        #suspect is a ChallengeUser in this case, scoring requires Player
        player = suspect.user.player_related.get()

        if suspect == None:
            return False, None

        last_chall = Challenge.objects.filter(Q(user_from__user=suspect) |
                Q(user_to__user=suspect)).order_by('-date')[0]
        if last_chall.user_from.user == suspect:
            participant = last_chall.user_from
        else:
            participant = last_chall.user_to
        #time interval could be made customizable
        if participant.seconds_took < 15:
            return True, player
        return False, None

    @classmethod
    def login_multiple_account(cls, **kwargs):
        #TODO test if multiple account suspicion
        return False, None
    #TODO add more rules for security

class Security(App):
    """Class that parses signals received from user activities
    and assigns penalty points as necessary"""

    @classmethod
    def penalise(cls, player, amount):
        coins = Coin.get('penalty')
        from wouso.core.scoring import score_simple
        if not coins is None:
            score_simple(player, coins, amount)

    @classmethod
    def activity_handler(cls, sender, **kwargs):
        action = kwargs.get('action', None)
        if action == 'chall-won':
            rules = SecurityConfig.objects.filter(applies_on='chall-won')
            for rule in rules:
                if rule.enabled:
                    guilty = SecurityInspector.check(rule, **kwargs)
                    if guilty:
                        #Get the player
                        player = kwargs.get('user_to', None).user.player_related.get()
                        cls.penalise(player, rule.penalty_value)

        if action == 'login':
            rules = models.SecurityConfig.objects.filter(applies_on='login')
            for rule in rules:
                if rule.enabled:
                    guilty = SecurityInspector.check(rule, **kwargs)
                    if guilty:
                        cls.penalise(player, rule.penalty_value)

def do_security_check(sender, **kwargs):
    Security.activity_handler(sender, **kwargs)

signals.addActivity.connect(do_security_check)
