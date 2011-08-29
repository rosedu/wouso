from django import forms
from wouso.core.qpool.models import Question

class QuestionForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea)

    def __init__(self, data=None): 
        super(QuestionForm, self).__init__(data)
        for i in filter(lambda a: a.startswith('answer_'), data.keys()):
            i = int(i[7:])
            self.fields['answer_%d' % i] = forms.CharField(max_length=100,
                                    widget=forms.Textarea, required=False)
            self.fields['correct_%d' % i] = forms.BooleanField(required=False)

    def clean(self):
        pass

    def save(self):
        pass