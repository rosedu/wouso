from django.db.models import Q
from wouso.core.config.models import BoolSetting
from wouso.core.app import App
from wouso.core.scoring.models import Coin, Formula
from wouso.interface.activity import signals

class SecurityInspector:
    #global check function dispatcher
    @classmethod
    def check(cls, rule, **kwargs):
        #convert - to _ from name of rule
        #Ex: chall-was-set-up -> chall_was_set_up
        return getattr(cls, rule.replace('-', '_'), False)(**kwargs)

    @classmethod
    def chall_was_set_up(cls, **kwargs):
        """
        Parse the chall-won activity message to
        check the time it took for the loser to finish the challenge
        """
        from wouso.games.challenge.models import Challenge
        suspect = kwargs.get('user_to', None)
        #suspect is a ChallengeUser in this case, scoring requires Player
        player = suspect.user.player_related.get()

        if suspect is None:
            return False, None

        last_chall = Challenge.objects.filter(Q(user_from__user=suspect) |
                Q(user_to__user=suspect)).order_by('-date')
        if not last_chall.count():
            return False, None
        last_chall = last_chall[0]
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

    SECURITY_RULES = [
        ('chall-was-set-up', 'Test if the challenge was lost on purpose', 'chall-won'),
        ('login-multiple-account', 'Test if user is using multiple accounts', 'login')
    ]


    @classmethod
    def penalise(cls, player, formula):
        coins = Coin.get('penalty')
        from wouso.core.scoring import score
        if not coins is None:
            score(user=player, game=None, formula=formula)

    @classmethod
    def activity_handler(cls, sender, **kwargs):
        action = kwargs.get('action', None)
        rules = filter(lambda x : x[2]==action, cls.SECURITY_RULES)
        for rule in rules:
            #check if rule is not disabled
            if not BoolSetting.objects.get(pk__startswith='disable-%s' % rule[0]).get_value():
                guilty, player = SecurityInspector.check(rule[0], **kwargs)
                if guilty:
                    formula = Formula.get('%s-infraction' % rule[0], 'general-infraction')
                    cls.penalise(player, formula)

def do_security_check(sender, **kwargs):
    Security.activity_handler(sender, **kwargs)

signals.addActivity.connect(do_security_check)
