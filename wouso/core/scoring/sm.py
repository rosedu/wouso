# TODO: why isn't this implemented as a class singleton, the same as God ?
import logging
from django.utils.translation import ugettext_noop
from django.db import models
from django.contrib.auth.models import User
from wouso.core import signals
from wouso.core.user.models import Player
from wouso.core.scoring.models import Coin, Formula, History
from wouso.core.god import God
from wouso.core.game import get_games, Game


class NotSetupError(Exception):
    pass


class InvalidFormula(Exception):
    pass


class FormulaParsingError(Exception):
    def __init__(self, formula):
        super(FormulaParsingError, self).__init__()
        self.formula = formula

    def __unicode__(self):
        return unicode(self.formula)


class InvalidScoreCall(Exception):
    pass


CORE_POINTS = ('points', 'gold', 'penalty')

# Utility functions
PHI = (1 + 5**0.5) / 2


def fib(n):
    return int(round((PHI**n - (1-PHI)**n) / 5**0.5))


# Setup
def check_setup():
    """ Check if the module has been setup """

    if Coin.get('points') is None:
        return False
    return True


def setup_scoring():

    """ Prepare database for Scoring """
    for cc in CORE_POINTS:
        if not Coin.get(cc):
            Coin.add(cc)
    # special case, gold is integer
    gold = Coin.get('gold')
    gold.integer = True
    gold.save()

    # iterate through games and register formulas
    for game in get_games():
        for formula in game.get_formulas():
            if not Formula.get(formula):
                Formula.add(formula)
    # add wouso formulas
    for formula in God.get_system_formulas():
        if not Formula.get(formula):
            Formula.add(formula)


def calculate(formula, **params):
    """ Calculate formula and return a dictionary of coin and amounts """
    formula = Formula.get(formula)
    if formula is None:
        raise InvalidFormula(formula)

    if not formula.expression:
        return {}

    return calculate_expression(formula.expression, formula, **params)


def calculate_expression(expression, formula=None, **params):
    """
    Calculate a formula defintion. Example of such defintions are:
        * points=50
        * points=10+{{level}}*100
        * gold=3;points=100

    Returns a dictionary with coins and values, example:
        {'points': 30, 'gold': 100}
    """
    ret = {}
    try:
        frml = expression.format(**params)
        # Python does not allow assignments inside eval
        # Using this workaround for now
        ass = frml.split(';')
        for a in ass:
            asp = a.split('=')
            coin = asp[0].strip()
            expr = '='.join(asp[1:])
            try:
                result = eval(expr)
            except ZeroDivisionError as e:
                result = 0
            ret[coin] = result
    except Exception as e:
        #logging.exception(e)
        raise FormulaParsingError(formula)
    return ret


def score(user, game, formula, external_id=None, percents=100, **params):
    """ Give amount of coin specified by the formula to the player.
     The amount can be affected by percents/100.
    """
    ret = calculate(formula, **params)

    if isinstance(ret, dict):
        for coin, amount in ret.items():
            score_simple(user, coin, amount, game, formula, external_id, percents=percents)


def timer(user, game, formula, default=300, **params):
    """ Compute a timer value, or return default
    """
    formula = Formula.get(formula)
    if formula is None:
        raise InvalidFormula(formula)
    if not formula.expression:
        return default

    values = calculate(formula, **params)
    if 'tlimit' in values:
        return values['tlimit']
    return default


def unset(user, game, formula, external_id=None, **params):
    """ Remove all history records by the external_id, formula and game given to the user """
    formula = Formula.get(formula)
    user = user.user.get_profile()  # make sure you are working on fresh Player
    for history in History.objects.filter(user=user, game=game.get_instance(), formula=formula, external_id=external_id):
        if history.coin.name == 'points':
            user.points -= history.amount
        history.delete()
    user.save()
    update_points(user, game)


def update_points(player, game):
    level = God.get_level_for_points(player.points)

    if level == player.level_no:
        return

    if level < player.level_no:
        action_msg = 'level-downgrade'
        signal_msg = ugettext_noop("downgraded to level {level}")
        signals.addActivity.send(sender=None, user_from=player,
                                 user_to=player, message=signal_msg,
                                 arguments=dict(level=level),
                                 game=game, action=action_msg)
    else:
        action_msg = 'level-upgrade'
        arguments = dict(level=level)
        # Check if the user has previously reached this level
        if level > player.max_level:
            # Update the maximum reached level
            player.max_level = level
            # Offer the corresponding amount of gold
            score(player, None, 'level-gold', external_id=level, level=level)

            signal_msg = ugettext_noop("upgraded to level {level} and received {amount} gold")
            amount = calculate('level-gold', level=level).get('gold', 0)
            arguments['amount'] = amount
        else:
            # The user should not receive additional gold
            signal_msg = ugettext_noop("upgraded back to level {level}")

        signals.addActivity.send(sender=None, user_from=player,
                                 user_to=player, message=signal_msg,
                                 arguments=arguments, game=None,
                                 action=action_msg)
    player.level_no = level
    player.save()


def score_simple(player, coin, amount, game=None, formula=None,
                 external_id=None, percents=100):

    """ Give amount of coin to the player.
    """
    if not isinstance(game, Game) and game is not None:
        game = game.get_instance()

    if not isinstance(player, Player):
        raise InvalidScoreCall()

    user = player.user
    player = user.get_profile()
    user = player.user

    coin = Coin.get(coin)
    formula = Formula.get(formula)

    computed_amount = 1.0 * amount * percents / 100
    hs = History.add(user=user, coin=coin, amount=computed_amount,
                     game=game, formula=formula, external_id=external_id, percents=percents)

    # update user.points asap
    if coin.name == 'points':
        if player.magic.has_modifier('top-disguise'):
            computed_amount = 1.0 * computed_amount * player.magic.modifier_percents('top-disguise') / 100

        player.points += computed_amount
        player.save()
        update_points(player, game)

    logging.debug("Scored %s with %f %s" % (user, computed_amount, coin))
    return hs


def history_for(user, game, external_id=None, formula=None, coin=None):
    """ Return all history entries for given (user, game) pair.
    """
    # TODO: check usage
    fltr = {}
    if external_id:
        fltr['external_id'] = external_id
    if formula:
        fltr['formula'] = Formula.get(formula)
    if coin:
        fltr['coin'] = Coin.get(coin)

    if not isinstance(game, Game):
        game = game.get_instance()

    if not isinstance(user, User):
        user = user.user

    try:
        return History.objects.filter(user=user, game=game, **fltr)
    except History.DoesNotExist:
        return None


def user_coins(user):
    """ Returns a dictionary with user coins """
    if not isinstance(user, User):
        user = user.user
    return History.user_coins(user)


def real_points(player):
    coin = Coin.get('points')
    result = History.objects.filter(user=player.user, coin=coin).aggregate(total=models.Sum('amount'))
    return result['total'] if result['total'] is not None else 0


def sync_user(player):
    """ Synchronise user points with database
    """
    coin = Coin.get('points')
    result = History.objects.filter(user=player.user, coin=coin).aggregate(total=models.Sum('amount'))
    points = result['total'] if result['total'] is not None else 0
    if player.points != points and not player.magic.has_modifier('top-disguise'):
        logging.debug('%s had %d instead of %d points' % (player, player.points, points))
        player.points = points
        player.level_no = God.get_level_for_points(player.points)
        player.save()


def sync_all_user_points():
    """ Synchronise points amounts for all players """
    for player in Player.objects.all():
        sync_user(player)


def first_login_check(sender, **kwargs):
    """ Callback function for addActivity signal """
    action = kwargs.get('action', None)
    player = kwargs['user_from']
    if action != 'login':
        return

    if player.activity_from.count() == 0:
        # kick some activity
        signal_msg = ugettext_noop('joined the game.')

        signals.addActivity.send(sender=None, user_from=player,
                                 user_to=player,
                                 message=signal_msg,
                                 game=None)

        # give some bonus points
        try:
            score(player, None, 'start-points')
        except InvalidFormula:
            logging.error('Formula start points is missing')

signals.addActivity.connect(first_login_check)
