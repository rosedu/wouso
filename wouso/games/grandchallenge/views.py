from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from models import  GrandChallengeGame, GrandChallengeUser
from wouso.interface import render_string

@login_required
def index(request):
    """ Shows all rounds played by the current user """
    profile = request.user.get_profile()
    gc_user = profile.get_extension(GrandChallengeUser)

    active = gc_user.get_active()
    played = gc_user.get_played()

    if not gc_user in GrandChallengeGame.base_query():
        messages.error(request, _('Ne pare rau, nu participi in turneu'))
        return render(request, 'grandchallenge/message.html')

    return render_to_response('grandchallenge/index.html',
            {'active': active, 'played': played, 'gcuser': gc_user, 'gc': GrandChallengeGame},
            context_instance=RequestContext(request))

def sidebar_widget(request):
    gc = GrandChallengeGame
    if gc.disabled():
        return ''
    gc_user = request.user.get_profile().get_extension(GrandChallengeUser)
    return render_string('grandchallenge/sidebar.html', {'gc': gc, 'gcuser': gc_user})
