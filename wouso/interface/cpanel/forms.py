from django import forms
from django.contrib.auth.models import User
from wouso.core.qpool.models import Question, Answer, Schedule, Category, Tag
from wouso.core.magic.models import Spell
from wouso.core.scoring.models import Formula
from wouso.core.security.models import Report

class QuestionForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea)
    active = forms.BooleanField(required=False)
    schedule = forms.DateField(required=False, input_formats=['%d.%m.%Y','%Y-%m-%d'], help_text='dd.mm.yyyy')
    category = forms.CharField(max_length=50, required=False)

    def __init__(self, data=None, instance=None, users=True):
        super(QuestionForm, self).__init__(data)
        if data is not None:
            for i in filter(lambda a: a.startswith('answer_'), data.keys()):
                i = int(i[7:])
                self.fields['answer_%d' % i] = forms.CharField(max_length=100,
                                        widget=forms.Textarea, required=False)
                self.fields['correct_%d' % i] = forms.BooleanField(required=False)

        alltags = instance.category.tag_set.all() if instance and instance.category else []
        self.fields['tags'] = forms.MultipleChoiceField(
                        choices=[(tag.name, tag.name) for tag in alltags],
                        widget=forms.SelectMultiple, required=False,
                        initial=[t.name for t in instance.tags.all()] if instance else {})
        self.instance = instance
        if users:
            self.fields['endorsed_by'] = forms.ModelChoiceField(queryset=User.objects.all(), required=False,
                                                                initial=instance.endorsed_by if instance else None)
            self.fields['proposed_by'] = forms.ModelChoiceField(queryset=User.objects.all(), required=False,
                                                                initial=instance.proposed_by if instance else None)
            self.users = True
        else:
            self.users = False

    def save(self):
        data = self.cleaned_data
        if self.instance is None:
            new = True
            self.instance = Question.objects.create()
            self.instance.category, nn = Category.objects.get_or_create(name=data['category'])
            self.instance.save()
        else:
            new = False

        for i in filter(lambda a: a.startswith('answer_'), data.keys()):
            i = int(i[7:])
            if not new:
                a = Answer.objects.get(pk=i)
            else:
                if data['answer_%d' % i] is None or not data['answer_%d' % i].strip():
                    continue
                a = Answer.objects.create(question=self.instance)
            a.text = data['answer_%d' % i]
            a.correct = data['correct_%d' % i]
            a.save()

        self.instance.text = data['text']
        self.instance.active = data['active']

        if self.instance.category.name == 'workshop':
            self.instance.answer_type = 'F'

        if self.users:
            self.instance.endorsed_by = data['endorsed_by']
            self.instance.proposed_by = data['proposed_by']

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
            tag, new = Tag.objects.get_or_create(name=t)
            self.instance.tags.add(tag)
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
    def __init__(self, data=None, instance=None, tags=[]):
        super(TagsForm, self).__init__(data)

        for tag in tags:
            self.fields['%s' % tag.name] = forms.BooleanField(initial=tag.active, required=True)

class AddTagForm(forms.ModelForm):
    class Meta:
        model = Tag

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions', 'is_staff', 'is_superuser']

class SpellForm(forms.ModelForm):
    class Meta:
        model = Spell

class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        
class EditReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ['user_to', 'user_from', 'text', 'timestamp' ] 
    def __init__(self, *args, **kwargs):
        super(EditReportForm, self).__init__(*args, **kwargs)
        self.fields['dibs'].label = "Dibs"
        self.fields['status'].label = "Status"
        self.fields['extra'].label = "Observations"
