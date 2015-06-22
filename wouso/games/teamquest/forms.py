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


class CreateGroupForm(forms.ModelForm):

	class Meta:
		model = TeamQuestGroup
		fields = ('name',)


class InvitePlayerForm(forms.ModelForm):

	class Meta:
		model = TeamQuestInvitation
		fields = ('to_user',)


class RequestToJoinForm(forms.ModelForm):

	class Meta:
		model = TeamQuestInvitationRequest
		fields = ('to_group',)
