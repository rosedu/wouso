from django import forms


class TopicCreateForm(forms.Form):
    topic = forms.CharField(label="Topic")
    message = forms.CharField(label="Message", widget=forms.Textarea())
