from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import render_string
from models import Quest, QuestGame, QuestUser
from forms import QuestForm

@login_required
def index(request):
    quest = QuestGame.get_current()

    if quest == None:
        return render_to_response('quest/none.html', context_instance=RequestContext(request))

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

    return render_to_response('quest/index.html',
            {'quest': quest, 'progress': quest_user, 'form': form, 'message': message},
            context_instance=RequestContext(request))

def sidebar_widget(request):
    quest = QuestGame.get_current()

    if quest is None:
        return ''

    quest_user = request.user.get_profile().get_extension(QuestUser)
    if not quest_user.started:
        quest_progress = None
    else:
        quest_progress = 1.0 * quest_user.current_level / quest.count * 100

    return render_string('quest/sidebar.html',
            {'quest': quest, 'quser': quest_user,
             'quest_progress': quest_progress,
             })
