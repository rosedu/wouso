from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.core.decorators import staff_required
from wouso.games.challenge.models import Challenge

@staff_required
def list_challenges(request):
    challenges = Challenge.objects.all().order_by('-date')
    context = {
       'challenges': challenges,
    }
    
    return render_to_response('challenge/cpanel/list_challenges.html', context,
                              context_instance=RequestContext(request))
