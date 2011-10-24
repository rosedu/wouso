from django.contrib import admin
from models import SpecialQuestTask, SpecialQuestUser, Invitation, SpecialQuestGroup


class SpecialQuestUserInline(admin.TabularInline):
    model = SpecialQuestUser

class SpecialQuestGroupAdmin(admin.ModelAdmin):
    inlines = [SpecialQuestUserInline]

admin.site.register(SpecialQuestUser)
admin.site.register(SpecialQuestTask)
admin.site.register(SpecialQuestGroup, SpecialQuestGroupAdmin)
admin.site.register(Invitation)
