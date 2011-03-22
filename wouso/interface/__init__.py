import logging
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext, Context

# Get a specific logger for this module
logger = logging.getLogger('interface')

# Theme
GAME_THEME='default'    # TODO: move it in God, or game settings

def render_response(template, request, data=None):
    """ Provide game context render_to response """
    config = {}
    config['theme'] = GAME_THEME
    
    context_instance = RequestContext(request, {'config': config})
        
    return render_to_response(template, 
            data,
            context_instance=context_instance
        )

def render_string(template, request, data=None):
    """ Provide game context render_to_string, used by widget generators """
    context_instance = Context(request)
    
    return render_to_string(template,
            data,
            context_instance=context_instance)
