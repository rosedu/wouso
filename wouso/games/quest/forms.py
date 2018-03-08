from django.forms import CharField, Form, ModelForm, TextInput
from models import Quest
from bootstrap3_datetime import widgets


class QuestForm(Form):
    answer = CharField(max_length=4000, widget=TextInput)


class QuestCpanel(ModelForm):
    class Meta:
        model = Quest
        widgets = {
            'start': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'end': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"})
        }
        exclude = ('order', 'registered',)
