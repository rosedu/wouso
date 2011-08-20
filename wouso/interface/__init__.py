import logging
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext, Context

# Get a specific logger for this module
logger = logging.getLogger('interface')

def render_response(template, request, data=None):
    """ Provide game context render_to response TODO: get rid of this"""

    return render_to_response(template, 
            data,
            context_instance=RequestContext(request)
        )

def render_string(template, data=None):
    """ Provide game context render_to_string, used by widget generators """
    
    return render_to_string(template,
            dictionary=data)
