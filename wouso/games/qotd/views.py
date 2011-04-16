from wouso.games.qotd.models import Question, Answer, QotdHistory
from games.qotd.forms import QotdForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from wouso import gamesettings as config
import datetime

@login_required # Note: this is a decorator, read more about it here: http://www.python.org/dev/peps/pep-0318/
def index(request):
    qotd = Question.get_for_today()
    if qotd == None:
        # Show some error
        return render_to_response('qotd/index.html', {'text': False}, context_instance=RequestContext(request))
    
    # Cannot answer twice
    if request.user.get_profile().has_answered_qotd:
        return HttpResponseRedirect("/qotd/done/")
        
    if request.method == "POST":
        form = QotdForm(qotd, request.POST)
        if form.is_valid():
            answers = qotd.answers()
            choice = int(form.cleaned_data['answers'])
            for a in qotd.answers():
                if a.id == choice:
                    # Save in history the response
                    qh = QotdHistory(user = request.user, question = qotd, date = qotd.date, choice = a, value = a.value)
                    qh.save()
                    # Modify has_answered
                    profile = request.user.get_profile()
                    profile.has_answered_qotd = True
                    profile.points = profile.points + config.QOTD_POINTS
                    profile.save()
                    return HttpResponseRedirect("/qotd/done/")
    else:
        form = QotdForm(qotd) 
        
    return render_to_response('qotd/index.html', 
            {'text': qotd.text, 'form': form}, 
            context_instance=RequestContext(request))
            
@login_required
def done(request):
    # Do not show results until done
    if not request.user.get_profile().has_answered_qotd:
        return HttpResponseRedirect("/qotd/")
    
    qotd = Question.get_for_today()
    answers = qotd.answers()
    try:
        qh = QotdHistory.objects.filter(question=qotd, user=request.user)[0]
    except:
        """ TODO: log this error """
        qh = QotdHistory(question=qotd, user=request.user, choice=answers[0], value = False)
        
    return render_to_response('qotd/done.html', 
            {'text': qotd.text, 'answers': answers, 'choice': qh.choice, 'valid': qh.value},
            context_instance=RequestContext(request))

