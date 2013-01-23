from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from piston.handler import BaseHandler
from piston.utils import rc
from models import Quest, QuestUser

class QuestAdminHandler(BaseHandler):
    """
    Get information about the quest module: a list of quests
    """
    methods_allowed = ('GET', )

    def read(self, request):
        quests = Quest.objects.all()
        return list(quests)


class QuestAdminUserHandler(BaseHandler):
    """
    Get and set information about specific user and quest
    """
    methods_allowed = ('GET', 'POST')

    def read(self, request, quest_id, username):
        quest = get_object_or_404(Quest, pk=quest_id)
        quest_user = get_object_or_404(User, username=username).get_profile().get_extension(QuestUser)

        if quest_user.current_quest != quest:
            return {'status': 'Not available'}

        return {'user': quest_user, 'status': 'Available', 'current_level': quest_user.current_level}

    def create(self, request, quest_id, username):
        if not request.user.has_perm('quest.change_quest'):
            return rc.FORBIDDEN

        quest = get_object_or_404(Quest, pk=quest_id)
        quest_user = get_object_or_404(User, username=username).get_profile().get_extension(QuestUser)

        if quest_user.current_quest != quest:
            return rc.NOT_FOUND

        new_level = quest_user.pass_level(quest)
        return {'current_level': new_level, 'user': {'id': quest_user.id, 'username': quest_user.user.username}}