from django import forms

class QuestForm(forms.Form):
    answer = forms.CharField(max_length=200)
