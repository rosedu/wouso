from django import forms
from models import TeamQuest
from bootstrap3_datetime import widgets


class AddTeamQuest(forms.ModelForm):
    number_of_levels = forms.IntegerField(label=unicode('Number of levels'), initial=4, min_value=0,
                                                                     required=True, help_text=" ")
    class Meta:
        model = TeamQuest
        widgets = {
                'start_time': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
                'end_time': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"})
                }
