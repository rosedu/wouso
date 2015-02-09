from django import forms
from ckeditor.widgets import CKEditorWidget

from interface.forum.models import Category, Forum


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        exclude = ('position')


class TopicCreateForm(forms.Form):
    topic = forms.CharField(label="Topic")
    text = forms.CharField(label="Message", widget=CKEditorWidget())


class PostCreateForm(forms.Form):
    message = forms.CharField(label="Message", widget=CKEditorWidget())
