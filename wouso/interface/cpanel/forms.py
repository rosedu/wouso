from django import forms
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from wouso.core.qpool.models import Question, Answer, Schedule, Category, Tag
from wouso.core.magic.models import Spell
from wouso.core.scoring.models import Formula
from wouso.core.security.models import Report
from wouso.core.user.models import Race, PlayerGroup
from wouso.interface.apps.pages.models import StaticPage, NewsItem


class MultipleField(forms.MultipleChoiceField):
    """No validation for choice."""
    def validate(self, value):
        return True

class QuestionForm(forms.Form):
    text = forms.CharField(max_length=2000, widget=forms.Textarea)
    active = forms.BooleanField(required=False)
    schedule = forms.DateField(required=False, input_formats=['%d.%m.%Y', '%Y-%m-%d'], help_text='dd.mm.yyyy')
    category = forms.CharField(max_length=100, required=False)

    def __init__(self, data=None, instance=None):
        super(QuestionForm, self).__init__(data)
        if data is not None:
            for i in filter(lambda a: a.startswith('answer_'), data.keys()):
                i = int(i[7:])
                self.fields['answer_%d' % i] = forms.CharField(max_length=500,
                                                               widget=forms.Textarea, required=False)
                self.fields['correct_%d' % i] = forms.BooleanField(required=False)
        categs = [(c.name, c.name.capitalize()) for c in Category.objects.all()]
        self.fields['category'] = forms.ChoiceField(choices=categs, initial=instance.category.name if instance and instance.category else None)
        alltags = instance.category.tag_set.all() if instance and instance.category else []
        self.fields['tags'] = MultipleField(
            choices=[(tag.name, tag.name) for tag in alltags],
            widget=forms.SelectMultiple, required=False,
            initial=[t.name for t in instance.tags.all()] if instance else {}
        )
        self.instance = instance
        self.fields['active'] = forms.BooleanField(required=False, initial=instance.active if instance else False)
        self.fields['answertype'] = forms.ChoiceField(choices=(("C", "multiple choice"), ("R", "single choice"),
                    ("F", "free text")), initial=instance.answer_type if instance else None)

    def save(self):
        data = self.cleaned_data
        # If new question create question instance. Otherwise drop all answers in order to replace them.
        if self.instance is None:
            self.instance = Question.objects.create()
        else:
            # Remove all answers and have them replaced.
            Answer.objects.filter(question=self.instance).delete()

        self.instance.category, nn = Category.objects.get_or_create(name=data['category'])

        for i in filter(lambda a: a.startswith('answer_'), data.keys()):
            i = int(i[7:])
            if data['answer_%d' % i] is None or not data['answer_%d' % i].strip():
                continue
            a = Answer.objects.create(question=self.instance)
            a.text = data['answer_%d' % i]
            a.correct = data['correct_%d' % i]
            a.save()

        self.instance.text = data['text']
        self.instance.active = data['active']

        self.instance.answer_type = data['answertype']
        if self.instance.category.name == 'workshop':
            self.instance.answer_type = 'F'

        # for qotd, scheduled
        if self.instance.category.name == 'qotd':
            sched = Schedule.objects.filter(question=self.instance)
            if sched:
                sched = sched[0]
            else:
                sched = Schedule.objects.create(question=self.instance)
            if data['schedule'] is None:
                sched.delete()
            else:
                sched.day = data['schedule']
                sched.save()
        # also do tags
        for t in self.instance.tags.all():
            self.instance.tags.remove(t)
        for t in data['tags']:
            try:
                # since the form does no validation on Tag choices,
                # we need to make sure they exist here
                tag = Tag.objects.get(name=t)
                self.instance.tags.add(tag)
            except:
                continue
        self.instance.save()
        return self.instance


class AnswerForm(forms.Form):
    def __init__(self, data=None, instance=None):
        super(AnswerForm, self).__init__(data)

        self.fields['new_answer_text'] = forms.CharField(max_length=100,
                                                         widget=forms.Textarea, required=False)
        self.fields['new_answer_correct'] = forms.BooleanField(required=False)

    def save(self, id=None):
        data = self.cleaned_data
        a = Answer.objects.create(question=id)
        a.text = data['new_answer_text']
        a.correct = data['new_answer_correct']
        a.save()


class TagsForm(forms.Form):
    def __init__(self, data=None, instance=None, tags=None):
        tags = tags or []
        super(TagsForm, self).__init__(data)

        for tag in tags:
            self.fields['%s' % tag.name] = forms.BooleanField(initial=tag.active, required=True)


class AddTagForm(forms.ModelForm):
    class Meta:
        model = Tag


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        widgets = {
            'password': forms.PasswordInput(),
        }
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password', 'confirm_password', 'is_active']

    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data


class SpellForm(forms.ModelForm):
    class Meta:
        model = Spell


class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula


class EditReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ['user_to', 'user_from', 'text', 'timestamp']

    def __init__(self, *args, **kwargs):
        super(EditReportForm, self).__init__(*args, **kwargs)
        self.fields['dibs'].label = "Dibs"
        self.fields['status'].label = "Status"
        self.fields['extra'].label = "Observations"


class TagForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.fields['questions'] = forms.MultipleChoiceField(choices=[(q.pk, q.text) for q in Question.objects.all()])
        self.fields['tag'] = forms.ChoiceField(choices=[(t.pk, t.name) for t in Tag.objects.all()
                                               .exclude(name__in=['qotd', 'quest', 'challenge'])])


class RoleForm(forms.ModelForm):
    class Meta:
        model = Group


class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        exclude = ['artifacts']


class PlayerGroupForm(forms.ModelForm):
    class Meta:
        model = PlayerGroup
        exclude = ['artifacts', 'owner']


class StaticPageForm(forms.ModelForm):
    class Meta:
        model = StaticPage


class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsItem


class KarmaBonusForm(forms.Form):
    def __init__(self, data=None, players=None):
        players = players or []
        super(KarmaBonusForm, self).__init__(data)
        for p in players:
            self.fields['%s' % p.user.username] = forms.IntegerField(label=unicode(p), initial=0, min_value=0, required=True, help_text=" ")
