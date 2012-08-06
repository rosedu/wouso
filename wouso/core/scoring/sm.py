# TODO: why isn't this implemented as a class singleton, the same as God ?
import logging
from django.utils.translation import ugettext_noop
from django.db import models
from django.contrib.auth.models import User
from wouso.core.user.models import Player
from wouso.core.scoring.models import Coin, Formula, History
from wouso.core.god import God
from wouso.core.game import get_games, Game
from wouso.interface.activity import signals

class NotSetupError(Exception): pass
class InvalidFormula(Exception): pass
class FormulaParsingError(Exception):
    def __init__(self, formula):
        super(FormulaParsingError, self).__init__()
        self.formula = formula
    def __unicode__(self):
        return unicode(self.formula)
class InvalidScoreCall(Exception): pass

CORE_POINTS = ('points','gold')

def check_setup():
    """ Check if the module has been setup """

    if Coin.get('points') is None:
        return False
    return True

def setup_scoring():
    """ Prepare database for Scoring """
    for cc in CORE_POINTS:
        if not Coin.get(cc):
            Coin.add(cc, name=cc)
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
        if not Formula.get(formula.id):
            Formula.add(formula)

def calculate(formula, **params):
    """ Calculate formula and return a dictionary of coin and amounts """
    formula = Formula.get(formula)
    if formula is None:
        raise InvalidFormula(formula)

    if not formula.formula:
        return {}

    ret = {}
    try:
        frml = formula.formula.format(**params)
        # Apparently, Python does not allow assignments inside eval
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
        logging.exception(e)
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

def unset(user, game, formula, external_id=None, **params):
    """ Remove all history records by the external_id, formula and game given to the user """
    for history in History.objects.filter(user=user, game=game.get_instance(), formula=formula, external_id=external_id):
        if history.coin.name == 'points':
            user.points -= history.amount
        history.delete()
    user.save()
    update_points(user, game)

def update_points(player, game):
    level = God.get_level_for_points(player.points)
    if level != player.level_no:
        if level < player.level_no:
            signal_msg = ugettext_noop("downgraded to level {level}")
        else:
            signal_msg = ugettext_noop("upgraded to level {level}")

        signals.addActivity.send(sender=None, user_from=player,
                             user_to=player, message=signal_msg,
                             arguments=dict(level=level),
                             game=game)
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

    coin = Coin.get(coin)
    formula = Formula.get(formula)

    computed_amount = 1.0 * amount * percents / 100
    hs = History.objects.create(user=user, coin=coin, amount=computed_amount,
        game=game, formula=formula, external_id=external_id, percents=percents)

    # update user.points asap
    if coin.name == 'points':
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

def sync_user(player):
    """ Synchronise user points with database
    """
    coin = Coin.get('points')
    result = History.objects.filter(user=player.user,coin=coin).aggregate(total=models.Sum('amount'))
    points = result['total'] if result['total'] is not None else 0
    if player.points != points:
        logging.debug('%s had %d instead of %d points' % (player, player.points, points))
        player.points = points
        player.level_no = God.get_level_for_points(player.points)
        player.save()

def sync_all_user_points():
    """ Synchronise points amounts for all players """
    for player in Player.objects.all():
        sync_user(player)
