from django.contrib import admin
from wouso.core.scoring.models import *

class FormulaAdmin(admin.ModelAdmin):
    list_display = ('id', 'formula', 'owner', 'description')

admin.site.register(Coin)
admin.site.register(Formula, FormulaAdmin)
admin.site.register(History)
