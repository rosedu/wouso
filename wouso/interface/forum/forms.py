from django import forms
from ckeditor.widgets import CKEditorWidget


class TopicCreateForm(forms.Form):
    topic = forms.CharField(label="Topic")
    text = forms.CharField(label="Message", widget=CKEditorWidget())


class PostCreateForm(forms.Form):
    message = forms.CharField(label="Message", widget=CKEditorWidget())
