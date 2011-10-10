from django import forms

class ChallengeForm(forms.Form):
    def __init__(self, challenge, data=None):
        super(ChallengeForm, self).__init__(data)
        
        for q in challenge.questions.all():
            field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=q.text)
            field.choices = [(a.id, a.text) for a in q.shuffled_answers]
            self.fields['answer_{id}'.format(id=q.id)] = field
        self.data = data
    
    def get_response(self):
        """ Parse response and return comprehensive list of ids """
        res = {}
        for f in filter(lambda name: name.startswith('answer_'), self.data):
            id = int(f[len('answer_'):])
            res[id] = [int(i) for i in self.data.getlist(f)]
        return res
