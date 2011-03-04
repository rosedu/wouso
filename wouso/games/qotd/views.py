from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from models import QotdUser, QotdGame
from forms import QotdForm

@login_required
def index(request):
    qotd = QotdGame.get_for_today()
    
    profile = request.user.get_profile()
    qotd_user = profile.get_extension(QotdUser)
    
    if qotd_user.has_answered:
        return HttpResponseRedirect(reverse('games.qotd.views.done'))
    
    if request.method == "POST":
        form = QotdForm(qotd, request.POST)
        if form.is_valid():
            choice = int(form.cleaned_data['answers'])
            QotdGame.answered(qotd_user, qotd, choice)
            return HttpResponseRedirect(reverse('games.qotd.views.done'))
    else:
        form = QotdForm(qotd) 
        
    return render_to_response('qotd/index.html', 
            {'question': qotd, 'form': form}, 
            context_instance=RequestContext(request))
            
@login_required
def done(request):
    # Do not show results until done
    if not request.user.get_profile().get_extension(QotdUser).has_answered:
        return HttpResponseRedirect(reverse("games.qotd.views.index"))
    
    qotd = QotdGame.get_for_today()
    return render_to_response('qotd/done.html',
            {'question': qotd, 'choice': request.user.get_profile().get_extension(QotdUser).last_answer},
            context_instance=RequestContext(request))
