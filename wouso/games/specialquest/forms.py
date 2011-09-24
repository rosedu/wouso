from django.forms import ModelForm, TextInput
from django.forms.fields import DateField
from models import SpecialQuestTask

class TaskForm(ModelForm):
    class Meta:
        model = SpecialQuestTask
        widgets = {'start_date': TextInput(attrs={'placeholder': 'yyyy-mm-dd'}),
                   'end_date': TextInput(attrs={'placeholder': 'yyyy-mm-dd'})}


