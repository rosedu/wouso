from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from models import GrandChallenge, GrandChallengeGame

@login_required
def index(request):
    """ Shows all rounds played by the current user """
    profile = request.user.get_profile()
    gc_user = profile.get_extension(GrandChallengeUser)

    active = GrandChallengeGame.get_active(gc_user)
    played = GrandChallengeGame.get_played(gc_user)

    if not gc_user in GrandChallengeGame.allUsers:
        return do_result(request, error='Ne pare rau, nu participi in turneu ')

    return render_to_response('grandchallenge/index.html',
            {'active': active, 'played': played, 'gcuser': gc_user},
            context_instance=RequestContext(request))

@login_required
def do_result(request, error='', message=''):
    return render_to_response('grandchallenge/message.html',
        {'error': error, 'message': message},
        context_instance=RequestContext(request))

def sidebar_widget(request):
    gc = GrandChallengeGame
    gc_user = request.user.get_profile().get_extension(GrandChallengeUser)
    return render_string('grandchallenge/sidebar.html', {'gchall': gc, 'gcuser': gcuser})
