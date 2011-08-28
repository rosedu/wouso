from django import forms
from wouso.core.qpool.models import Tag


class QuestionForm(forms.Form):

    text = forms.CharField(max_length=500, widget=forms.Textarea)
    answer_type = forms.ChoiceField(choices=(('R', 'Single'), ('C','Multiple')))

    def __init__(self, nr_ans=5, data=None): 
        super(QuestionForm, self).__init__(data)
        self.answers = []
        for i in range(5):
            self.fields['answer_%d' % i] = forms.CharField(max_length=100,
                                    widget=forms.Textarea, required=False)
            self.answers.append(self.fields['answer_%d' % i])
            self.fields['correct_%d' % i] = forms.BooleanField(required=False, label="Correct?")
        alltags = Tag.objects.all()
        self.fields['tags'] = forms.MultipleChoiceField(
                        choices=[(tag.name, tag.name) for tag in alltags],
                        widget=forms.SelectMultiple, required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        answer_type = cleaned_data.get('answer_type')
        nr = 0
        for i in range(5):
            if cleaned_data.get('correct_%d' % i) is True:
                nr += 1
        if nr == 0:
            raise forms.ValidationError("No correct answer!")
        elif nr > 1 and answer_type == 'R':
            raise forms.ValidationError("Must have only one correct answer!")
        elif nr == 1 and answer_type == 'C':
            raise forms.ValidationError("Must have more than one correct answer!")
        return cleaned_data
