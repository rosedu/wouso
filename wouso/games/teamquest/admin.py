from django.contrib import admin
from models import TeamQuest, TeamQuestUser, TeamQuestGroup, TeamQuestInvitation, TeamQuestInvitationRequest

admin.site.register(TeamQuestInvitation)
admin.site.register(TeamQuestInvitationRequest)
