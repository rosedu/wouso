from django.contrib import admin
from wouso.core.scoring.models import *
from django import forms


class FormulaForm(forms.ModelForm):
    formula = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Formula


class FormulaAdmin(admin.ModelAdmin):
    list_display = ('id', 'expression', 'owner', 'description')
    form = FormulaForm


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'formula', 'external_id', 'amount', 'coin')
    list_filter = ('formula', 'external_id', 'coin')


admin.site.register(Coin)
admin.site.register(Formula, FormulaAdmin)
admin.site.register(History, HistoryAdmin)
