from django import forms
from models import Quest

class QuestForm(forms.Form):
    answer = forms.CharField(max_length=200)

class QuestCpanel(forms.ModelForm):
    class Meta:
        model = Quest