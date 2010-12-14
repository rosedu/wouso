from models import WQuest, UserProgress, QuestForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

def index(request):
    quest = WQuest.get_current()
    
    if quest == None:
        return render_to_response('wquest/none.html', {}, 
                context_instance=RequestContext(request))
                
    progress = UserProgress.get_progress(request.user, quest)
    message = ""
    if request.method == "POST":
        form = QuestForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            check = progress.check_answer(answer)
            if not check:
                message = "Wrong answer, try again"
        else:
            message = "Invalid form"
    
    form = QuestForm()
    
    return render_to_response('wquest/index.html', 
            {'quest': quest, 'progress': progress, 'form': form, 'message': message}, 
            context_instance=RequestContext(request))
