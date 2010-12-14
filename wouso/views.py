# views for the base project
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.tzinfo import LocalTimezone
from wouso.core.profile.models import UserProfile
import datetime

def homepage(request):
    """ First page shown """
    d = datetime.datetime.now() + datetime.timedelta(minutes=-10)
    # Get all users online in the last 10 minutes
    online_users = UserProfile.objects.filter(last_online__gt=d).order_by('-last_online')
    
    return render_to_response('site_base.html', 
            {'online_users': online_users}, 
            context_instance=RequestContext(request))
