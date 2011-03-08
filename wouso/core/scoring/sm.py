from django.contrib.auth.models import User
from wouso.core.game import get_games
from wouso.core.scoring.models import *
from wouso.core import logger

class NotSetupError(Exception): pass
class InvalidFormula(Exception): pass
class FormulaParsingError(Exception): pass

CORE_POINTS = ('points',)

#def __init__(self):
#    if not Scoring.check_setup():
#        raise NotSetupError('Please setup the Scoring Module, using '+
#        '\n\t'+'python core/scoring/default_setup.py')

def check_setup():
    """ Check if the module has been setup """
    
    if Coin.get('points') is None:
        return False
    return True

def setup():
    """ Prepare database for Scoring """
    for cc in CORE_POINTS:
        if not Coin.get(cc):
            Coin.add(cc, name=cc)
    
    # iterate through games and register formulas
    for game in get_games():
        for formula in game.get_formulas():
            if not Formula.get(formula.id):
                Formula.add(formula)

def calculate(formula, **params):
    """ Calculate formula """
    formula = Formula.get(formula)
    if formula is None:
        raise InvalidFormula(formula)
    
    ret = {}
    try:    
        frml = formula.formula.format(**params)
        # Apparently, Python does not allow assignments inside eval
        # Using this workaround for now
        ass = frml.split(',')
        for a in ass:
            asp = a.split('=')
            coin = asp[0].strip()
            expr = '='.join(asp[1:])
            result = eval(expr)
            ret[coin] = result
    except Exception as e:
        raise FormulaParsingError(e)
        
    return ret
    
def score(user, game, formula, external_id=None, **params):
    ret = calculate(formula, **params)
        
    if isinstance(ret, dict):
        for coin, amount in ret.items():
            score_simple(user, coin, amount, game, formula, external_id)
            
def score_simple(user, coin, amount, game=None, formula=None, 
    external_id=None):
    
    if not isinstance(game, Game):
        game = game.get_instance()
    
    if not isinstance(user, User):
        user = user.user
            
    coin = Coin.get(coin)
    formula = Formula.get(formula) 
    
    hs = History.objects.create(user=user, coin=coin, amount=amount,
        game=game, formula=formula, external_id=external_id)
    
    return hs
    
def history_for(user, game, external_id=None, formula=None, coin=None):
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
