from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from models import QotdUser, QotdGame
from forms import QotdForm

@login_required
def index(request):
    if QotdGame.disabled():
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))
    qotd = QotdGame.get_for_today()

    profile = request.user.get_profile()
    qotd_user = profile.get_extension(QotdUser)

    if qotd_user.has_answered:
        return HttpResponseRedirect(reverse('games.qotd.views.done'))

    if qotd is None:
        form = None

    elif request.method == "POST":
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
    if QotdGame.disabled():
            return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))
    # Do not show results until done
    if not request.user.get_profile().get_extension(QotdUser).has_answered:
        return HttpResponseRedirect(reverse("games.qotd.views.index"))

    qotd = QotdGame.get_for_today()
    user = request.user.get_profile().get_extension(QotdUser)
    choice = user.last_answer
    ans = [a for a in qotd.answers if a.id == choice]
    if ans:
        ans = ans[0]
        valid = ans.correct
    else:
        ans = None
        valid = False

    return render_to_response('qotd/done.html',
            {'question': qotd, 'choice': ans, 'valid': valid,},
            context_instance=RequestContext(request))

def sidebar_widget(request):
    qotd = QotdGame.get_for_today()
    qotd_user = request.user.get_profile().get_extension(QotdUser)

    if qotd_user.has_answered:
        time_passed = datetime.now() - qotd_user.last_answered
        if time_passed > timedelta(seconds=120): # two minutes
            return ''
    return render_to_string('qotd/sidebar.html', {'question': qotd, 'quser': qotd_user, 'qotd': QotdGame})
