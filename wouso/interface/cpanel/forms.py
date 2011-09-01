from django import forms
from wouso.core.qpool.models import Question, Answer

class QuestionForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea)

    def __init__(self, data=None, instance=None): 
        super(QuestionForm, self).__init__(data)
        if data is not None:
            for i in filter(lambda a: a.startswith('answer_'), data.keys()):
                i = int(i[7:])
                self.fields['answer_%d' % i] = forms.CharField(max_length=100,
                                        widget=forms.Textarea, required=False)
                self.fields['correct_%d' % i] = forms.BooleanField(required=False)
        self.instance = instance

    def save(self):
        if not self.instance:
            # TODO: add new 
            return
        data = self.cleaned_data
        for i in filter(lambda a: a.startswith('answer_'), data.keys()):
            i = int(i[7:])
            a = Answer.objects.get(pk=i)
            a.text = data['answer_%d' % i]
            a.correct = data['correct_%d' % i]
            a.save()
        print data
        self.instance.text = data['text']
        self.instance.save()