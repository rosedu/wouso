from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View
from wouso.core.ui import register_sidebar_block
from wouso.core.user.models import Player
from wouso.core.qpool.models import Question, Answer, Category
from django.http import HttpResponseRedirect, HttpResponse

from models import *


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    quest_user = user.get_profile().get_extension(TeamQuestUser)
    quest = TeamQuestGame.get_current()

    group = quest_user.group
    status = TeamQuestStatus.objects.filter(group=group, quest=quest)
    if status.count():
        status = status[0]
        progress = status.progress * 1.0 / quest.total_points * 100
    else:
        progress = 0
        status = None

    return render_to_string('teamquest/sidebar.html',
                            {'quest': quest, 'tquser': quest_user,
                             'group': quest_user.group, 'status':status,
                             'progress': progress,
                             })

register_sidebar_block('teamquest', sidebar_widget)
