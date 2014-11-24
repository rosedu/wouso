from django import forms

from wouso.interface.apps.files.models import File, FileCategory


class FileForm(forms.ModelForm):
    class Meta:
        model = File

        exclude = ['type']

    def save(self, commit=True):
        data = self.cleaned_data

        self.instance.save()

        # Get type from file name
        name = data['file'].name
        type = name.split('.')[-1].upper()
        self.instance.type = type
        self.instance.save()

        return self.instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = FileCategory
