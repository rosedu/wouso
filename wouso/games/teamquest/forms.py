from django import forms
from models import *


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
