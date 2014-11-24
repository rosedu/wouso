from django import forms

from wouso.interface.apps.lesson.models import Lesson, LessonCategory
from games.quiz.models import Quiz


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson

    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)

        self.fields['quiz_show_time'].label = "Show quiz after (minutes)"
        self.fields['quiz'].queryset = Quiz.objects.filter(type='L')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = LessonCategory
        exclude = ('order')
