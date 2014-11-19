from django import forms
from wouso.interface.apps.lesson.models import Lesson, LessonCategory


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson


class CategoryForm(forms.ModelForm):
    class Meta:
        model = LessonCategory
