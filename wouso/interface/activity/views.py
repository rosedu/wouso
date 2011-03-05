from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import Activity
from wouso.interface import logger

def activities(request):
    list = Activity.get_activities(0,10)
    return render_to_response('activity.html',
            {'activity': list},
            context_instance=RequestContext(request))
