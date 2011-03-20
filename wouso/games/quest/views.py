from django.contrib.auth.decorators import login_required
from wouso.interface import render_response
from models import Quest, QuestGame, QuestUser
from forms import QuestForm

@login_required
def index(request):
    quest = QuestGame.get_current()
    
    if quest == None:
        return render_response('quest/none.html', request)
    
    quest_user = request.user.get_profile().get_extension(QuestUser)
    if quest_user.current_quest is None:
        quest_user.set_current(quest)
        
    message = ''
    if request.method == "POST":
        form = QuestForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            check = quest.check_answer(quest_user, answer)
            if not check:
                message = "Wrong answer, try again"
        else:
            message = "Invalid form"
    
    form = QuestForm()
    
    return render_response('quest/index.html', request, 
            {'quest': quest, 'progress': quest_user, 'form': form, 'message': message})
