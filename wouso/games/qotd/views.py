from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from models import QotdUser

@login_required
def index(request):
    #qotd = Question.get_for_today()
    
    profile = request.user.get_profile()
    qotd_user = profile.get_extension(QotdUser)
    
    if qotd_user.has_answered:
        return HttpResponseRedirect(reverse('games.qotd.views.done'))
        
    return render_to_response('qotd/index.html', 
            {'text': 'Cate?', 'form': ''}, 
            context_instance=RequestContext(request))
            
@login_required
def done(request):
    # Do not show results until done
    if not request.user.get_profile().has_answered_qotd:
        return HttpResponseRedirect("/qotd/")
