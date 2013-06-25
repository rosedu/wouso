from django.forms import CharField, Form, ModelForm, Textarea
from django.contrib.admin import widgets
from models import Quest

class QuestForm(Form):
    answer = CharField(max_length=4000, widget=Textarea)

class QuestCpanel(ModelForm):
    class Meta:
        model = Quest
        widgets = {
                   'start': widgets.AdminSplitDateTime,
                   'end': widgets.AdminSplitDateTime
                   }
        exclude = ('order', 'registered',)
