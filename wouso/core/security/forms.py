from django import forms


class UserReportForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
