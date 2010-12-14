from wouso.extra.activity.models import Activity, ChallengeActivity
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def get_activities(start, end, Q):
    # list of specific activities
    specific_activities = []
    
    # list of general activities
    activities = Activity.objects.select_related(depth=2).filter(Q).order_by('-specific_activity__datetime')[start:end]

    # convert to specific class and get extra info
    for a in activities:
        a.specific_activity.name_from = a.specific_activity.user.get_full_name()
        if isinstance(a.specific_activity, ChallengeActivity):
            a.specific_activity.name_to = a.specific_activity.cuser.get_full_name()
            
        specific_activities.append(a.specific_activity)
        
    return specific_activities

def public(request):
    # interval
    start = int(request.GET.get('start', '0'))
    end = int(request.GET.get('end', str(int(start) + 10)))
    
    ca_ctype = ContentType.objects.get_for_model(ChallengeActivity)
    a = get_activities(start, end, 
                       Q(content_type=ca_ctype))
    
    return render_to_response('activity/public.html',
                              {'activities': a},
                              context_instance=RequestContext(request))
@login_required   
def private(request):
    # interval
    start = int(request.GET.get('start', '0'))
    end = int(request.GET.get('end', str(int(start) + 10)))
    
    ca_ctype = ContentType.objects.get_for_model(ChallengeActivity)
    a = get_activities(start, end,
                       (Q(content_type=ca_ctype) & Q(specific_activity__challengeactivity__cuser=request.user.id)) | 
                       Q(specific_activity__user=request.user.id))
    
    return render_to_response('activity/public.html',
                              {'activities': a},
                              context_instance=RequestContext(request))
