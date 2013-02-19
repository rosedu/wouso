from django import forms
from wouso.core.qpool.models import Question, Answer
from wouso.core.user.models import Player
from models import SpecialChallenge


class CreateForm(forms.Form):
    player_to = forms.ModelChoiceField(Player.objects.all())


class ConfigureForm(forms.ModelForm):
    class Meta:
        model = SpecialChallenge
        fields = ('amount', )


class QuestionForm(forms.ModelForm):
    DEFAULT_ANSWERS = 5

    class Meta:
        model = Question
        fields = ('text',)

    def __init__(self, data=None, instance=None, **kwargs):
        super(QuestionForm, self).__init__(data=data, instance=instance, **kwargs)
        data = data if data else {}
        if instance is None:
            for i in range(self.DEFAULT_ANSWERS):
                self.fields['answer_%d' % i] = forms.CharField(max_length=400, required=False, initial=data.get('answer_%d' %i, ''))
                self.fields['correct_%d' % i] = forms.BooleanField(required=False, label="Correct?", initial=data.get('correct_%d' %i, False))
        else:
            for i, a in enumerate(instance.answers):
                self.fields['answer_%d' % i] = forms.CharField(max_length=400, required=False, initial=data.get('answer_%d' %i, a.text))
                self.fields['correct_%d' % i] = forms.BooleanField(required=False, label="Correct?", initial=data.get('correct_%d' %i, a.correct))
        self.fields['answer_new'] = forms.CharField(max_length=400, required=False, initial=data.get('answer_new', ''))
        self.fields['correct_new'] = forms.BooleanField(required=False, label="Correct?", initial=data.get('correct_new', False))

    def save(self, commit=True):
        new = self.instance.pk is None
        question = super(QuestionForm, self).save(commit=commit)
        if new:
            for i in range(self.DEFAULT_ANSWERS):
                a_text = self.cleaned_data.get('answer_%d' % i).strip()
                a_correct = self.cleaned_data.get('correct_%d' % i)
                if a_text:
                    Answer.objects.create(question=question, text=a_text, correct=a_correct)
        else:
            for i, a in enumerate(question.answers):
                a_text = self.cleaned_data.get('answer_%d' % i).strip()
                a_correct = self.cleaned_data.get('correct_%d' % i)
                if a_text:
                    a.text, a.correct = a_text, a_correct
                    a.save()
                else:
                    a.delete()
        # Also check answer_new
        a_text = self.cleaned_data.get('answer_new').strip()
        a_correct = self.cleaned_data.get('correct_new')
        if a_text:
            Answer.objects.create(question=question, text=a_text, correct=a_correct)

        return question