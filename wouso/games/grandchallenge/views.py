from django.http import HttpResponseRedirect, Http404
from models import GrandChallenge, GrandChallengeGame

@login_required
def index(request):
    gchalls = GrandChallenge.getchallenges()

@login_required
def gchalls(request):
    gchalls = GrandChallenge.objects.all()
    return render_to_response('cpanel/grandchallenges.html',
                            {'gchalls': gchalls},
                            context_instance=RequestContext(request))
