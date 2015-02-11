from django import forms

from ckeditor.widgets import CKEditorWidget

from wouso.interface.apps.lesson.models import Lesson, LessonCategory, LessonTag
from games.quiz.models import Quiz


class CategoryForm(forms.ModelForm):
    class Meta:
        model = LessonCategory
        exclude = ('order')


class TagForm(forms.ModelForm):
    class Meta:
        model = LessonTag
        exclude = ('order')


class AddLessonForm(forms.Form):
    def __init__(self, data=None, instance=None):
        super(AddLessonForm, self).__init__(data)

        self.fields['name'] = forms.CharField(max_length=100, required=True)
        self.fields['tag'] = forms.ChoiceField(choices=[(t.name, t.name) for t in LessonTag.objects.all()],
                                               required=True)
        self.fields['youtube_url'] = forms.URLField(required=False)
        self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget())
        quizzes = [('--None--', '--None--')]
        quizzes.extend([(q.name, q.name) for q in Quiz.objects.filter(type='L')])
        self.fields['quiz'] = forms.ChoiceField(choices=quizzes, required=False)
        self.fields['quiz_show_time'] = forms.IntegerField(required=True, initial=5)
        self.fields['active'] = forms.BooleanField(required=False, initial=False)

        self.instance = instance

    def save(self):
        data = self.cleaned_data

        self.instance = Lesson.objects.create()

        self.instance.name = data['name']
        self.instance.tag = LessonTag.objects.get(name=data['tag']) if data['tag'] else None
        self.instance.youtube_url = data['youtube_url']
        self.instance.content = data['content']
        self.instance.quiz = Quiz.objects.get(name=data['quiz']) if data['quiz'] != '--None--' else None
        self.instance.quiz_show_time = int(data['quiz_show_time'])
        self.instance.active = data['active']

        self.instance.save()
        return self.instance


class EditLessonForm(forms.Form):
    def __init__(self, data=None, instance=None):
        super(EditLessonForm, self).__init__(data)

        self.fields['name'] = forms.CharField(max_length=100, required=True, initial=instance.name)
        categories = [(c.name, c.name.capitalize()) for c in LessonCategory.objects.all()]
        self.fields['category'] = forms.ChoiceField(choices=categories,
                                                    initial=instance.tag.category.name if instance and instance.tag else None)
        tags = instance.tag.category.tags.all() if instance and instance.tag else []
        self.fields['tag'] = forms.ChoiceField(required=True,
                                               choices=[(t.name, t.name.capitalize()) for t in tags],
                                               initial=(instance.tag.name,
                                                        instance.tag.name) if instance and instance.tag else None)
        self.fields['youtube_url'] = forms.URLField(required=False, initial=instance.youtube_url)
        self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=instance.content)
        quizzes = [(q.name, q.name) for q in Quiz.objects.filter(type='L')]
        quizzes.append(('--None--', '--None--'))
        self.fields['quiz'] = forms.ChoiceField(choices=quizzes, required=False,
                                                initial=instance.quiz.name if instance and instance.quiz else None)
        self.fields['quiz_show_time'] = forms.IntegerField(required=True,
                                                           initial=instance.quiz_show_time if instance and instance.quiz_show_time else 5)
        self.fields['active'] = forms.BooleanField(required=False, initial=instance.active if instance else False)

        self.instance = instance

    def save(self):
        data = self.cleaned_data

        self.instance.name = data['name']
        self.instance.content = data['content']
        self.instance.tag = LessonTag.objects.get(name=data['tag']) if data['tag'] else None
        self.instance.youtube_url = data['youtube_url']
        self.instance.quiz = Quiz.objects.get(name=data['quiz']) if data['quiz'] != '--None--' else None
        self.instance.quiz_show_time = data['quiz_show_time']
        self.instance.active = data['active']

        self.instance.save()
        return self.instance
