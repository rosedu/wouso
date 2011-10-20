from django.contrib import admin
from models import SpecialQuestTask, SpecialQuestUser, Invitation, SpecialQuestGroup

admin.site.register(SpecialQuestUser)
admin.site.register(SpecialQuestTask)
admin.site.register(SpecialQuestGroup)
admin.site.register(Invitation)
