from core.profile.models import Message
from django.forms import ModelForm

class MessageForm(ModelForm):
    """ Message form for composing / replying """
    class Meta:
        model = Message
        fields = ('subject', 'text')
