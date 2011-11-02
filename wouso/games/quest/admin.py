from django.contrib import admin
from models import Quest, QuestUser

class QUAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'current_quest', 'current_level', 'started_time', 'finished_time')
    list_filter = ('current_quest', 'current_level', 'finished')

admin.site.register(Quest)

admin.site.register(QuestUser, QUAdmin)
