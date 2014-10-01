from django import forms


class QuizForm(forms.Form):
    def __init__(self, quiz, data=None):
        super(QuizForm, self).__init__(data)

        for q in quiz.questions.all():
            field = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label=q.text)
            field.choices = [(a.id, a.text) for a in q.shuffled_answers]
            self.fields['answer_{id}'.format(id=q.id)] = field
        self.data = data
