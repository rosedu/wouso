from django import forms

class ChallengeForm(forms.Form):
    def __init__(self, challenge, data=None):
        super(ChallengeForm, self).__init__(data)
        
        for q in challenge.questions.all():
            field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=q.text)
            field.choices = [(a.id, a.text) for a in question.answers]
            self.fields['answer_{id}'.format(id=q.id)] = field
        self.data = data
    
    def get_response(self):
        return self.data
