from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from wouso.interface import render_response, render_string
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
        
    return render_response('qotd/index.html', 
            request,
            {'question': qotd, 'form': form})
            
@login_required
def done(request):
    # Do not show results until done
    if not request.user.get_profile().get_extension(QotdUser).has_answered:
        return HttpResponseRedirect(reverse("games.qotd.views.index"))
    
    qotd = QotdGame.get_for_today()
    choice = request.user.get_profile().get_extension(QotdUser).last_answer
    return render_response('qotd/done.html',
            request,
            {'question': qotd, 'choice': choice, 
            'valid': qotd.answers[choice].correct
            })

def sidebar_widget(request):
    qotd = QotdGame.get_for_today()
    qotd_user = request.user.get_profile().get_extension(QotdUser)
    
    return render_string('qotd/sidebar.html', {'question': qotd, 'quser': qotd_user})
