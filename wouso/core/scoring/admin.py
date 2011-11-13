from django.contrib import admin
from wouso.core.scoring.models import *

class FormulaAdmin(admin.ModelAdmin):
    list_display = ('id', 'formula', 'owner', 'description')

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'formula', 'external_id', 'amount', 'coin')
    list_filter = ('formula', 'external_id', 'coin')
admin.site.register(Coin)
admin.site.register(Formula, FormulaAdmin)
admin.site.register(History, HistoryAdmin)
