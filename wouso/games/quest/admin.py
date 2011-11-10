from django.contrib import admin
from models import Quest, QuestUser, QuestResult

class QUAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'current_quest', 'current_level', 'started_time', 'finished_time')
    list_filter = ('current_quest', 'current_level', 'finished')

class QRAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'level')
    list_filter = ('quest', 'level')

admin.site.register(Quest)
admin.site.register(QuestResult, QRAdmin)

admin.site.register(QuestUser, QUAdmin)
